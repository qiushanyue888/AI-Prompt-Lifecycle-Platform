from fastapi import FastAPI
from pydantic import BaseModel
import pymysql
import requests

app = FastAPI(title="AI提示词工具箱")
# 定义新增提示词的请求体格式
class TemplateCreate(BaseModel):
    title: str
    content: str
    category: str = "通用"

# 数据库连接函数
def get_db():
    return pymysql.connect(
        host="localhost",
        port=3306,
        user="root",
        password="123456",
        database="prompt_box",
        charset="utf8mb4"
    )

# 第一个接口：获取所有提示词模板
@app.get("/api/templates")
def get_templates():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, content, category, create_time FROM prompt_template ORDER BY id DESC")
    results = cursor.fetchall()

    data = []
    for row in results:
        data.append({
            "id": row[0],
            "title": row[1],
            "content": row[2],
            "category": row[3],
            "create_time": str(row[4])
        })

    cursor.close()
    conn.close()
    return {"code": 200, "data": data, "msg": "获取成功"}
# 第二个接口：新增提示词模板
@app.post("/api/templates")
def add_template(item: TemplateCreate):
    conn = get_db()
    cursor = conn.cursor()
    sql = "INSERT INTO prompt_template (title, content, category) VALUES (%s, %s, %s)"
    cursor.execute(sql, (item.title, item.content, item.category))
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return {"code": 201, "data": {"id": new_id, "title": item.title}, "msg": "添加成功"}
# 根路径，测试用
@app.get("/")
def root():
    return {"message": "AI提示词工具箱后端运行成功！"}


# 第三个接口：根据ID删除一条提示词模板
@app.delete("/api/templates/{template_id}")
def delete_template(template_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM prompt_template WHERE id = %s", (template_id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return {"code": 404, "msg": "提示词不存在"}

    cursor.execute("DELETE FROM prompt_template WHERE id = %s", (template_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return {"code": 200, "msg": f"提示词 {template_id} 已删除"}


# 第四个接口：根据ID修改一条提示词模板
@app.put("/api/templates/{template_id}")
def update_template(template_id: int, item: TemplateCreate):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM prompt_template WHERE id = %s", (template_id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return {"code": 404, "msg": "提示词不存在"}

    sql = "UPDATE prompt_template SET title = %s, content = %s, category = %s WHERE id = %s"
    cursor.execute(sql, (item.title, item.content, item.category, template_id))
    conn.commit()
    cursor.close()
    conn.close()
    return {"code": 200, "msg": f"提示词 {template_id} 已更新"}


# ================= AI 对话接口 =================

# 阿里云密钥与接口地址
API_KEY = "sk-ws-H.RXLMYYH.clP5.MEQCIGmMDgyBpF3f3MbIz9tJjMPR_yq2X3hawNXPZj-WbRNWAiBx0ljWDLlPvZ-6MXxolfwwTxeX1b9ChK-CMhcMONKPFw"
API_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"


class ChatRequest(BaseModel):
    prompt: str


@app.post("/api/ai/chat")
def ai_chat(req: ChatRequest):
    # 构造请求内容
    payload = {
        "model": "qwen-turbo",
        "input": {"messages": [{"role": "user", "content": req.prompt}]},
        "parameters": {"result_format": "text"}
    }
    headers = {"Authorization": f"Bearer {API_KEY}"}

    # 调用AI接口
    try:
        resp = requests.post(API_URL, json=payload, headers=headers)
        resp_data = resp.json()
        ai_answer = resp_data["output"]["text"].strip()
    except Exception as e:
        return {"code": 500, "msg": f"AI调用失败: {str(e)}"}

    # 保存对话记录到数据库
    try:
        conn = get_db()
        cursor = conn.cursor()
        sql = "INSERT INTO ai_eval_record (input_content, eval_result, record_type) VALUES (%s, %s, 'chat')"
        cursor.execute(sql, (req.prompt, ai_answer))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"数据库保存出错（chat）: {e}")

    return {"code": 200, "data": {"answer": ai_answer}, "msg": "AI回答成功"}


# ================= AI 评测接口 =================

class EvalRequest(BaseModel):
    question: str
    standard_answer: str
    user_answer: str


@app.post("/api/ai/evaluate")
def ai_evaluate(req: EvalRequest):
    # 1. 构造给裁判模型的打分指令
    eval_prompt = f"""严格阅卷，满分10分，只输出数字，不要任何文字解释。
打分规则：
1. 答案完全正确、完整：9-10分
2. 大体正确，少量细节缺失：6-8分
3. 一半内容对一半错：3-5分
4. 核心知识点错误、完全答偏：0-2分

题目：{req.question}
标准答案：{req.standard_answer}
考生回答：{req.user_answer}
仅输出0-10之间的单个数字。"""

    # 2. 调用千问API
    payload = {
        "model": "qwen-turbo",
        "input": {"messages": [{"role": "user", "content": eval_prompt}]},
        "parameters": {"result_format": "text"}
    }
    headers = {"Authorization": f"Bearer {API_KEY}"}

    try:
        resp = requests.post(API_URL, json=payload, headers=headers)
        resp_data = resp.json()
        score = resp_data["output"]["text"].strip()
    except Exception as e:
        return {"code": 500, "msg": f"AI评测调用失败: {str(e)}"}

    # 3. 保存评测记录到数据库
    try:
        conn = get_db()
        cursor = conn.cursor()
        sql = "INSERT INTO ai_eval_record (input_content, eval_result, score, record_type) VALUES (%s, %s, %s, 'evaluate')"
        cursor.execute(sql, (req.question, req.user_answer, float(score)))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"数据库保存出错（evaluate）: {e}")

    # 4. 返回分数
    return {"code": 200, "data": {"score": score}, "msg": "评测完成"}