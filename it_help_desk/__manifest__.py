{
    "name": "IT Help Desk",
    "version": "19.0.1.0.0",
    "author": "AESL",
    "summary": "IT Asset issue resolvement and related tasks",
    "category": "Operations",
    "depends": ["base", "mail", "it_asset_management"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "security/ir.model.access.csv",
        "data/sequence.xml",
        'data/mail_template.xml',
        'views/res_partner_views.xml',
        "views/help_desk_views.xml",
    ],
    "installable": True,
    "application": True,
}
