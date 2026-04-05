from flask import Flask, render_template_string
app = Flask(__name__)

UI = '''
<body style="background:#000;color:#fff;text-align:center;font-family:sans-serif;padding-top:80px;">
    <h1 style="color:#e50914;font-size:3em;">MALLY <span style="color:#fff">PRO</span></h1>
    <p style="color:#444;letter-spacing:2px;">CLOUD DOWNLOADER & CUTTER</p>
    <form action="/run" method="post" style="margin-top:30px;">
        <input type="text" name="titulo" placeholder="Título de la Serie" required 
               style="width:320px;padding:15px;margin:10px;background:#111;color:#fff;border:1px solid #222;border-radius:10px;"><br>
        <input type="text" name="link" placeholder="URL del Video" required 
               style="width:320px;padding:15px;margin:10px;background:#111;color:#fff;border:1px solid #222;border-radius:10px;"><br>
        <button type="submit" style="background:#e50914;color:#fff;padding:18px 50px;border:none;border-radius:10px;font-weight:bold;cursor:pointer;margin-top:20px;box-shadow: 0 0 20px rgba(229,9,20,0.2);">
            INICIAR TRABAJO
        </button>
    </form>
</body>
'''

@app.route('/')
def index(): return render_template_string(UI)
