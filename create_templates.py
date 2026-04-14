import os

base_dir = r"d:\Quantix\Quantix\templates\municipality_portal"
dirs = ['stalls', 'locations', 'vendors', 'officers', 'violations', 'reports']

for d in dirs:
    os.makedirs(os.path.join(base_dir, d), exist_ok=True)

files = {
    'base.html': '''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>بوابة البلدية | Q-Zone</title>
    <link href="https://api.fontshare.com/v2/css?f[]=cabinet-grotesk@800,700,500,400&f[]=satoshi@400,500,700&display=swap" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/remixicon@3.5.0/fonts/remixicon.css" rel="stylesheet">
    <style>
        :root {
            --base: #F8F9FA; --surface: #FFFFFF; --surface-hover: #F1F3F5;
            --text-main: #0B0F19; --text-muted: #64748B;
            --accent: #111827; --accent-hover: #374151;
            --success: #10B981; --warning: #F59E0B; --danger: #EF4444; 
            --radius-md: 12px; --radius-xl: 24px;
            --font-display: 'Cabinet Grotesk', sans-serif;
            --font-body: 'Satoshi', sans-serif;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: var(--font-body); }
        body { background: var(--base); color: var(--text-main); }
        .app-shell { max-width: 480px; margin: 0 auto; height: 100dvh; display: flex; flex-direction: column; background: var(--base); position: relative; }
        header { background: var(--accent); color: white; padding: 14px 20px; display: flex; justify-content: space-between; align-items: center; }
        main { flex: 1; padding: 20px 16px 80px; overflow-y: auto; }
        .bottom-nav { position: absolute; bottom: 0; left: 0; right: 0; background: white; border-top: 1px solid #eee; display: flex; justify-content: space-around; padding: 10px; }
        .bottom-nav a { display: flex; flex-direction: column; align-items: center; color: var(--text-muted); text-decoration: none; font-size: 12px; font-weight: 600; }
        .bottom-nav a.active { color: var(--accent); }
        .bottom-nav i { font-size: 24px; }
        .card { background: white; padding: 20px; border-radius: 16px; margin-bottom: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
        h1, h2, h3 { font-family: var(--font-display); }
        .btn { display: inline-flex; align-items: center; justify-content: center; padding: 12px; background: var(--accent); color: white; text-decoration: none; border-radius: 8px; font-weight: bold; border:none; cursor:pointer;}
        .btn-success { background: var(--success); }
        .btn-danger { background: var(--danger); }
        .form-control { width: 100%; padding: 10px; margin-bottom: 15px; border-radius: 8px; border: 1px solid #ddd; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
        .badge { padding: 4px 8px; border-radius: 20px; font-size: 12px; }
        .badge-pending { background: #fef3c7; color: #d97706; }
        .badge-active { background: #d1fae5; color: #059669; }
    </style>
</head>
<body>
    <div class="app-shell">
        <header>
            <div>
                <h1 style="font-size:18px;">Q-Zone</h1>
                <span style="font-size:12px; opacity:0.7;">بوابة البلدية</span>
            </div>
            <a href="{% url 'accounts:logout' %}" style="color:white; text-decoration:none;"><i class="ri-logout-box-r-line"></i></a>
        </header>
        <main>
            {% block content %}{% endblock %}
        </main>
        <div class="bottom-nav">
            <a href="{% url 'municipality_portal:dashboard' %}"><i class="ri-dashboard-line"></i>الرئيسية</a>
            <a href="{% url 'municipality_portal:stall_list' %}"><i class="ri-store-2-line"></i>البسطات</a>
            <a href="{% url 'municipality_portal:location_list' %}"><i class="ri-map-pin-line"></i>المواقع</a>
            <a href="{% url 'municipality_portal:vendor_list' %}"><i class="ri-user-2-line"></i>التجار</a>
        </div>
    </div>
</body>
</html>
''',
    'dashboard.html': '''{% extends 'municipality_portal/base.html' %}
{% block content %}
<h2>مرحباً، لوحة القيادة</h2>
<br>
<div class="grid">
    <a href="{% url 'municipality_portal:stall_list' %}" class="card" style="text-decoration:none; color:inherit;">
        <h3>{{ total_stalls }}</h3><p>بسطة</p>
    </a>
    <a href="{% url 'municipality_portal:vendor_list' %}" class="card" style="text-decoration:none; color:inherit;">
        <h3>{{ total_vendors }}</h3><p>تاجر</p>
    </a>
    <a href="{% url 'municipality_portal:officer_list' %}" class="card" style="text-decoration:none; color:inherit;">
        <h3>{{ total_officers }}</h3><p>مفتش</p>
    </a>
    <a href="{% url 'municipality_portal:violation_list' %}" class="card" style="text-decoration:none; color:inherit;">
        <h3>{{ total_violations }}</h3><p>مخالفة</p>
    </a>
    <a href="{% url 'municipality_portal:reports' %}" class="card" style="text-decoration:none; color:inherit; grid-column: span 2;">
        <h3>تقارير وإحصائيات</h3><p>عرض التفاصيل</p>
    </a>
</div>
{% endblock %}
''',
    'stalls/list.html': '''{% extends 'municipality_portal/base.html' %}
{% block content %}
<h2>البسطات</h2>
<br>
{% for stall in stalls %}
<a href="{% url 'municipality_portal:stall_detail' stall.pk %}" class="card" style="display:block; text-decoration:none; color:inherit;">
    <strong>{{ stall.owner.user.get_full_name }}</strong>
    <p>{{ stall.category.name }}</p>
    <span class="badge {% if stall.status == 'active' %}badge-active{% else %}badge-pending{% endif %}">{{ stall.get_status_display }}</span>
</a>
{% endfor %}
{% endblock %}
''',
    'stalls/detail.html': '''{% extends 'municipality_portal/base.html' %}
{% block content %}
<h2>تفاصيل البسطة</h2>
<br>
<div class="card">
    <p><strong>المالك:</strong> {{ stall.owner.user.get_full_name }}</p>
    <p><strong>الحالة:</strong> {{ stall.get_status_display }}</p>
    <p><strong>التصنيف:</strong> {{ stall.category.name }}</p>
    <p><strong>الوصف:</strong> {{ stall.description }}</p>
    {% if stall.location %}<p><strong>الموقع:</strong> {{ stall.location.name }}</p>{% endif %}

    <hr style="margin:15px 0">
    <div class="grid">
    {% if stall.status == 'pending' %}
        <a href="{% url 'municipality_portal:stall_approve' stall.pk %}" class="btn btn-success">موافقة</a>
        <a href="{% url 'municipality_portal:stall_reject' stall.pk %}" class="btn btn-danger">رفض</a>
    {% else %}
        <a href="{% url 'municipality_portal:stall_suspend' stall.pk %}" class="btn btn-danger">إيقاف</a>
        <a href="{% url 'municipality_portal:subscription_create' stall.pk %}" class="btn btn-success" style="font-size:12px;">تسجيل اشتراك</a>
    {% endif %}
    </div>
</div>
{% endblock %}
''',
    'stalls/approve.html': '''{% extends 'municipality_portal/base.html' %}
{% block content %}
<h2>موافقة على البسطة</h2>
<br>
<form method="post" class="card">
    {% csrf_token %}
    {{ form.as_p }}
    {{ location_form.as_p }}
    <button type="submit" class="btn btn-success" style="width:100%">موافقة وتعيين الموقع</button>
</form>
{% endblock %}
''',
    'stalls/reject.html': '''{% extends 'municipality_portal/base.html' %}
{% block content %}
<h2>رفض البسطة</h2>
<br>
<form method="post" class="card">
    {% csrf_token %}
    <label>سبب الرفض</label><br>
    <textarea name="reason" class="form-control" required></textarea>
    <button type="submit" class="btn btn-danger" style="width:100%">تأكيد الرفض</button>
</form>
{% endblock %}
''',
    'stalls/suspend.html': '''{% extends 'municipality_portal/base.html' %}
{% block content %}
<h2>إيقاف البسطة</h2>
<br>
<form method="post" class="card">
    {% csrf_token %}
    <p style="margin-bottom:10px;">هل أنت متأكد من إيقاف هذه البسطة؟</p>
    <button type="submit" class="btn btn-danger" style="width:100%">تأكيد الإيقاف</button>
</form>
{% endblock %}
''',
    'stalls/subscription_form.html': '''{% extends 'municipality_portal/base.html' %}
{% block content %}
<h2>إضافة اشتراك</h2>
<br>
<form method="post" class="card">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit" class="btn btn-success" style="width:100%">حفظ</button>
</form>
{% endblock %}
''',
    'locations/list.html': '''{% extends 'municipality_portal/base.html' %}
{% block content %}
<h2>المواقع <a href="{% url 'municipality_portal:location_create' %}" class="btn btn-success" style="float:left; padding:5px 10px; font-size:12px;">+ إضافة</a></h2>
<br><br>
{% for loc in locations %}
<div class="card">
    <strong>{{ loc.name }}</strong>
    <p style="font-size:12px;">{{ loc.capacity }} بسطة | السعة</p>
    <a href="{% url 'municipality_portal:location_edit' loc.pk %}" style="font-size:12px; color:var(--accent); display:inline-block; margin-top:5px;">تعديل</a>
</div>
{% endfor %}
{% endblock %}
''',
    'locations/form.html': '''{% extends 'municipality_portal/base.html' %}
{% block content %}
<h2>{{ title }}</h2>
<br>
<form method="post" class="card">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit" class="btn" style="width:100%">حفظ</button>
</form>
{% endblock %}
''',
    'vendors/list.html': '''{% extends 'municipality_portal/base.html' %}
{% block content %}
<h2>التجار</h2>
<br>
{% for vendor in vendors %}
<a href="{% url 'municipality_portal:vendor_detail' vendor.pk %}" class="card" style="display:block; text-decoration:none; color:inherit;">
    <strong>{{ vendor.user.get_full_name }}</strong>
    <p>الهوية: {{ vendor.national_id }}</p>
</a>
{% endfor %}
{% endblock %}
''',
    'vendors/detail.html': '''{% extends 'municipality_portal/base.html' %}
{% block content %}
<h2>تفاصيل التاجر</h2>
<br>
<div class="card">
    <p><strong>الاسم:</strong> {{ vendor.user.get_full_name }}</p>
    <p><strong>الهوية:</strong> {{ vendor.national_id }}</p>
    <p><strong>الحالة:</strong> {{ vendor.get_status_display }}</p>
</div>
{% endblock %}
''',
    'officers/list.html': '''{% extends 'municipality_portal/base.html' %}
{% block content %}
<h2>المفتشين <a href="{% url 'municipality_portal:officer_create' %}" class="btn btn-success" style="float:left; padding:5px 10px; font-size:12px;">+ إضافة</a></h2>
<br><br>
{% for officer in officers %}
<div class="card">
    <strong>{{ officer.user.get_full_name }}</strong>
    <p>الرقم: {{ officer.badge_number }}</p>
</div>
{% endfor %}
{% endblock %}
''',
    'officers/form.html': '''{% extends 'municipality_portal/base.html' %}
{% block content %}
<h2>{{ title }}</h2>
<br>
<form method="post" class="card">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit" class="btn" style="width:100%">حفظ</button>
</form>
{% endblock %}
''',
    'violations/list.html': '''{% extends 'municipality_portal/base.html' %}
{% block content %}
<h2>المخالفات</h2>
<br>
{% for v in violations %}
<div class="card">
    <strong>{{ v.stall.owner.user.get_full_name }}</strong>
    <p>{{ v.get_violation_type_display }}</p>
    <p style="font-size:12px; color:var(--text-muted);">بواسطة: {{ v.officer.user.get_full_name }}</p>
</div>
{% endfor %}
{% endblock %}
''',
    'reports/index.html': '''{% extends 'municipality_portal/base.html' %}
{% block content %}
<h2>التقارير والإحصائيات</h2>
<br>
<div class="card">
    <p><strong>الاشتراكات النشطة:</strong> {{ active_subscriptions }}</p>
    <p><strong>اشتراكات تنتهي قريباً:</strong> {{ expiring_soon }}</p>
</div>
{% endblock %}
'''
}

for rel_path, content in files.items():
    with open(os.path.join(base_dir, rel_path), 'w', encoding='utf-8') as f:
        f.write(content)

print('Done creating templates.')
