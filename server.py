from flask import Flask, render_template_string
app = Flask(__name__)

HTML_UI = '''
<body style="background:#000;color:#fff;text-align:center;padding-top:50px;font-family:sans-serif;">
    <h1 style="color:#e50914; font-size:3.5em;">MALLY <span style="color:#fff">DL</span></h1>
    <p style="color:#888;">MODO CLOUD-STREAMING ACTIVADO</p>
    
    <form action="/process" method="post" style="margin-top:30px;">
        <input type="text" name="titulo" placeholder="Título de la Película" required 
               style="width:80%; max-width:400px; padding:15px; border-radius:10px; background:#111; color:#fff; border:1px solid #333; margin-bottom:15px;"><br>
        
        <input type="text" name="link" placeholder="Pega el link aquí (YouTube/IG/etc)" required 
               style="width:80%; max-width:400px; padding:15px; border-radius:10px; background:#111; color:#fff; border:1px solid #333; margin-bottom:25px;"><br>
        
        <button type="submit" style="background:#e50914; color:#fff; padding:20px 60px; font-weight:bold; border-radius:10px; border:none; cursor:pointer; box-shadow: 0 5px 15px rgba(229,9,20,0.4);">
            DESCARGAR Y SUBIR
        </button>
    </form>
</body>
'''

@app.route('/')
def index():
    return render_template_string(HTML_UI)
