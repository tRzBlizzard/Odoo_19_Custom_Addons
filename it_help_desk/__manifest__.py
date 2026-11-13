{
    "name": "IT Help Desk",
    "version": "19.0.1.0.0",
    "author": "AESL",
    "summary": "IT Asset issue resolvement and related tasks",
    "category": "Operations",
    "depends": ["base", "mail", "it_asset_management"],
    "data": [
        "security/ir.model.access.csv",
        "data/sequence.xml",
        'views/res_partner_views.xml',
        "views/help_desk_views.xml",
    ],
    "installable": True,
    "application": True,
}
