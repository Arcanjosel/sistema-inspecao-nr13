from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QMessageBox, QLineEdit, QLabel, QFormLayout, QComboBox
)
from database.connection import DatabaseConnection
from controllers.auth_controller import AuthController

class DebugWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Debug - Visualizar Usuários")
        self.setMinimumSize(800, 500)
        self.db = DatabaseConnection()
        self.auth_controller = AuthController()
        self.setup_ui()
        self.load_users()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Formulário de cadastro de admin
        form_layout = QFormLayout()
        self.nome_input = QLineEdit()
        self.email_input = QLineEdit()
        self.senha_input = QLineEdit()
        self.senha_input.setEchoMode(QLineEdit.Password)
        self.empresa_input = QLineEdit()
        self.tipo_input = QComboBox()
        self.tipo_input.addItems(["admin", "cliente"])
        form_layout.addRow(QLabel("<b>Cadastro de Usuário</b>"))
        form_layout.addRow("Nome:", self.nome_input)
        form_layout.addRow("E-mail:", self.email_input)
        form_layout.addRow("Senha:", self.senha_input)
        form_layout.addRow("Empresa:", self.empresa_input)
        form_layout.addRow("Tipo:", self.tipo_input)
        self.cadastrar_btn = QPushButton("Cadastrar Usuário")
        self.cadastrar_btn.clicked.connect(self.cadastrar_admin)
        form_layout.addRow(self.cadastrar_btn)
        layout.addLayout(form_layout)

        # Botão de atualizar
        self.refresh_btn = QPushButton("Atualizar Lista")
        self.refresh_btn.clicked.connect(self.load_users)
        layout.addWidget(self.refresh_btn)

        # Tabela de usuários
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nome", "Email", "Tipo Acesso", "Empresa", "Ativo", "Senha Hash"
        ])
        layout.addWidget(self.table)

    def load_users(self):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, nome, email, tipo_acesso, empresa, ativo, senha_hash FROM usuarios")
            rows = cursor.fetchall()
            self.table.setRowCount(len(rows))
            for row_idx, row in enumerate(rows):
                for col_idx, value in enumerate(row):
                    self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
            cursor.close()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar usuários: {str(e)}")

    def cadastrar_admin(self):
        nome = self.nome_input.text().strip()
        email = self.email_input.text().strip()
        senha = self.senha_input.text().strip()
        empresa = self.empresa_input.text().strip() or None
        tipo = self.tipo_input.currentText()
        if not nome or not email or not senha:
            QMessageBox.warning(self, "Atenção", "Preencha todos os campos para cadastrar um usuário.")
            return
        sucesso, mensagem = self.auth_controller.criar_usuario(
            nome=nome,
            email=email,
            senha=senha,
            tipo_acesso=tipo,
            empresa=empresa
        )
        if sucesso:
            QMessageBox.information(self, "Sucesso", "Usuário cadastrado com sucesso!")
            self.nome_input.clear()
            self.email_input.clear()
            self.senha_input.clear()
            self.empresa_input.clear()
            self.tipo_input.setCurrentIndex(0)
            self.load_users()
        else:
            QMessageBox.critical(self, "Erro", f"Erro ao cadastrar: {mensagem}")