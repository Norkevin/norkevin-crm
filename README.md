# Norkevin CRM

CRM para Norkevin Photography. Web app en Flask + SQLite con tus clientes reales.

## Features

- Calendar con bodas agendadas
- Pipeline de Leads (nuevo / contactado / consulta / cerrado)
- Lista de Clients confirmados
- Jobs (bodas con equipo asignado)
- Payments (pendientes y cobrados)
- Settings con tus cuentas bancarias y paquetes

## Stack

- **Backend**: Flask 3.1
- **DB**: SQLite local
- **Frontend**: Tailwind CSS
- **Puerto**: 8765

## Como correr

```bash
pip install flask
python app.py
```

Abrir http://localhost:8765

## Estructura

```
crm_norkevin/
├── app.py              # Backend Flask
├── data/
│   └── crm.db         # SQLite (con tus clientes reales)
├── templates/
│   ├── base.html       # Layout con sidebar negro + dorado
│   ├── calendar.html   # Vista principal
│   ├── leads.html      # Pipeline de leads
│   ├── clients.html    # Lista de clientes
│   ├── jobs.html       # Bodas agendadas
│   ├── payments.html   # Pagos pendientes/cobrados
│   └── settings.html   # Config
└── static/
```

## Tu data

Los clientes reales vienen del wiki de Norkevin Photography:
- Carlos Zelaya (4-jul-2026)
- Geraldine Barberena (18-jul-2026)
- Cindy Cerezo (25-jul-2026)
- Karen Sandoval (1-ago-2026)
- Daniel Dubuc (15-ago-2026)
- Y mas...

---
*Norkevin CRM v0.1 - 3 jul 2026*
