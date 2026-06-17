from flask import Flask, jsonify, request, Response
import requests

app = Flask(__name__)

# السيرفر الأصلي المستهدف للمحاكاة الكاملة
TARGET_SERVER = "http://kalalook.blog:8080"
TARGET_USER = "0176436959603"
TARGET_PASS = "2442668892"

@app.route('/player_api.php')
def proxy_api():
    # سحب جميع الأوامر والطلبات القادمة من تطبيق Lion TV تلقائياً
    action = request.args.get('action', '')
    stream_id = request.args.get('stream_id', '')
    
    # بناء الرابط لإرساله للسيرفر الأصلي مع بياناتك الصحيحة لجلب كل شيء
    target_url = f"{TARGET_SERVER}/player_api.php?username={TARGET_USER}&password={TARGET_PASS}"
    if action:
        target_url += f"&action={action}"
    if stream_id:
        target_url += f"&stream_id={stream_id}"
        
    try:
        # الاتصال بالسيرفر الأصلي وجلب القنوات الحقيقية كاملة
        response = requests.get(target_url, timeout=10)
        return Response(response.content, status=response.status_code, content_type=response.headers.get('content-type'))
    except Exception as e:
        return jsonify({"error": "تعذر الاتصال بالسيرفر الأصلي حالياً", "details": str(e)}), 500

@app.route('/live/<username>/<password>/<int:stream_id>.ts')
def proxy_stream(username, password, stream_id):
    # توجيه رابط البث المباشر لأي قناة يختارها المستخدم فوراً وبدون تقطيع (302 Redirect)
    actual_stream_url = f"{TARGET_SERVER}/live/{TARGET_USER}/{TARGET_PASS}/{stream_id}.ts"
    return "", 302, {"Location": actual_stream_url}

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
