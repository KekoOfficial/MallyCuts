from flask import Flask, render_template_string, request
import config

app = Flask(__name__)

HTML_UI = '''
<body style="background:#000;color:#fff;text-align:center;padding-top:50px;font-family:sans-serif;">
    <h1 style="color:#e50914; font-size:3.5em;">MALLY <span style="color:#fff">PRO</span></h1>
    <form action="/upload" method="post" enctype="multipart/form-data" style="margin-top:30px;">
        <input type="text" name="titulo" placeholder="Título de la Película" required 
               style="width:80%; max-width:400px; padding:15px; border-radius:10px; background:#111; color:#fff; border:1px solid #333; margin-bottom:20px;">
        <br>
        <label style="background:#e50914; color:#fff; padding:20px 50px; cursor:pointer; font-weight:bold; border-radius:10px; display:inline-block;">
            SUBIR SERIE
            <input type="file" name="file" accept="video/*" onchange="this.form.submit()" style="display:none;">
        </label>
    </form>
</body>
'''

@app.route('/')
def index():
    return render_template_string(HTML_UI)
