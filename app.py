from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///checklists.db'  # Usando SQLite para persistência dos dados
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo de Checklist
class Checklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehicle_type = db.Column(db.String(100))
    plate_number = db.Column(db.String(10))
    items_checked = db.Column(db.String(200))  # Vamos armazenar como string para simplificação

    def __repr__(self):
        return f"<Checklist {self.vehicle_type} - {self.plate_number}>"

# Rota para sincronizar os dados com o servidor
@app.route("/sync", methods=["POST"])
def sync():
    try:
        data = request.get_json()
        # Extrair dados do checklist
        vehicle_type = data.get('vehicle_type')
        plate_number = data.get('plate_number')
        items_checked = ",".join(data.get('items_checked', []))  # Converter lista para string

        # Criar um novo registro no banco de dados
        new_checklist = Checklist(
            vehicle_type=vehicle_type,
            plate_number=plate_number,
            items_checked=items_checked
        )
        db.session.add(new_checklist)
        db.session.commit()

        return jsonify({"message": "Checklist sincronizado com sucesso!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Rota para o formulário online
@app.route("/online_form.html")
def online_form():
    return render_template("online_form.html")

# Rota para o formulário offline
@app.route("/offline_form.html")
def offline_form():
    return render_template("offline_form.html")

# Página inicial
@app.route("/")
def index():
    return render_template("index.html")

# Rota para processar o formulário enviado via POST
@app.route("/submit", methods=["POST"])
def submit_form():
    try:
        vehicle_type = request.form.get("vehicle_type")
        plate_number = request.form.get("plate_number")
        items_checked = request.form.getlist("items_checked")

        new_checklist = Checklist(
            vehicle_type=vehicle_type,
            plate_number=plate_number,
            items_checked=",".join(items_checked)
        )
        db.session.add(new_checklist)
        db.session.commit()

        return render_template("success.html", message="Checklist enviado com sucesso!")
    except Exception as e:
        return render_template("error.html", error=str(e))

# Nova rota para listar todas as placas enviadas
@app.route("/list_plates", methods=["GET"])
def list_plates():
    # Consulta todos os registros do banco de dados
    checklists = Checklist.query.all()
    return render_template("list_plates.html", checklists=checklists)

if __name__ != "__main__":
    with app.app_context():
        db.create_all()