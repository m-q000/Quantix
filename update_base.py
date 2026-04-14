import os, re

op_base = r'd:\Quantix\Quantix\templates\officer_portal\base.html'
mp_base = r'd:\Quantix\Quantix\templates\municipality_portal\base.html'

with open(op_base, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace officer stuff with municipality stuff
content = content.replace('بوابة المفتش', 'بوابة البلدية')
content = content.replace('officer_portal:', 'municipality_portal:')
content = content.replace('officer-header', 'municipality-header')
content = content.replace('officer-chip', 'municipality-chip')
content = content.replace('ri-shield-check-line', 'ri-building-line')
content = content.replace('{{ user.officer_profile.badge_number }}', '{{ user.get_full_name|default:user.username }}')
content = content.replace('{% if user.officer_profile %}', '{% if user.is_authenticated %}')

nav_html = """
        <nav class="bottom-nav">
            <a href="{% url 'municipality_portal:dashboard' %}" class="nav-item">
                <i class="ri-home-5-line"></i>
                <span>الرئيسية</span>
            </a>
            <a href="{% url 'municipality_portal:stall_list' %}" class="nav-item">
                <i class="ri-store-2-line"></i>
                <span>البسطات</span>
            </a>
            <a href="{% url 'municipality_portal:location_list' %}" class="nav-item">
                <i class="ri-map-pin-line"></i>
                <span>المواقع</span>
            </a>
            <a href="{% url 'municipality_portal:vendor_list' %}" class="nav-item">
                <i class="ri-user-2-line"></i>
                <span>التجار</span>
            </a>
        </nav>
"""

content = re.sub(r'<nav class="bottom-nav">.*?</nav>', nav_html, content, flags=re.DOTALL)

with open(mp_base, 'w', encoding='utf-8') as f:
    f.write(content)
print('Updated base.html successfully')
