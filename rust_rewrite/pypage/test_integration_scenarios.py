#!/usr/bin/env python3
"""
Integration Scenarios Test Suite - Tests real-world scenarios combining multiple features.
"""

import sys
import os

# Import the Rust module directly from the current directory
sys.path.insert(0, os.path.dirname(__file__))
import pypage

# Test counters
passed = 0
total = 0

def test_case(template, expected, description):
    """Helper function to run a test case"""
    global passed, total
    total += 1
    
    try:
        result = pypage.pypage_process(template, {})
        if result == expected:
            print(f"✅ Test {total:2d}: PASS - {description}")
            passed += 1
        else:
            print(f"❌ Test {total:2d}: FAIL - {description}")
            if len(expected) < 500 and len(result) < 500:
                print(f"    Template: {repr(template)}")
                print(f"    Expected: {repr(expected)}")
                print(f"    Got:      {repr(result)}")
            else:
                print(f"    Expected length: {len(expected)}, Got length: {len(result)}")
    except Exception as e:
        print(f"❌ Test {total:2d}: ERROR - {description}")
        print(f"    Template: {repr(template)}")
        print(f"    Error:    {e}")

def test_web_page_template():
    """Test web page template generation"""
    print("\nTesting web page template generation...")
    print("=" * 60)
    
    # Simple HTML page with variables
    html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
</head>
<body>
    <h1>{{ heading }}</h1>
    {% if show_nav %}
    <nav>
        {% for link in nav_links %}
        <a href="{{ link['url'] }}">{{ link['text'] }}</a>
        {% endfor %}
    </nav>
    {% endif %}
    <main>{{ content }}</main>
</body>
</html>
""".strip()
    
    expected_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Test Page</title>
</head>
<body>
    <h1>Welcome</h1>
    
    <nav>
        
        <a href="/home">Home</a>
        
        <a href="/about">About</a>
        
    </nav>
    
    <main>Hello World</main>
</body>
</html>
""".strip()
    
    test_case(
        "{% capture title %}Test Page{% endcapture %}" +
        "{% capture heading %}Welcome{% endcapture %}" +
        "{% capture show_nav %}True{% endcapture %}" +
        "{% capture nav_links %}[{'url': '/home', 'text': 'Home'}, {'url': '/about', 'text': 'About'}]{% endcapture %}" +
        "{% capture content %}Hello World{% endcapture %}" +
        html_template,
        expected_html,
        "Web page template with navigation"
    )

def test_data_report_generation():
    """Test data report generation scenarios"""
    print("\nTesting data report generation...")
    print("=" * 60)
    
    # Sales report template
    report_template = """
{% def format_currency amount %}${{ "%.2f"|format(amount) }}{% enddef %}
{% def calculate_total items %}{{ sum(item['amount'] for item in items) }}{% enddef %}

SALES REPORT
============
{% for category, items in sales_data.items() %}
{{ category.upper() }}:
{% for item in items %}
  - {{ item['name'] }}: {{ format_currency(item['amount']) }}
{% endfor %}
  Subtotal: {{ format_currency(calculate_total(items)) }}

{% endfor %}
GRAND TOTAL: {{ format_currency(sum(calculate_total(items) for items in sales_data.values())) }}
""".strip()
    
    # This is a simplified version for our test
    simple_report = """
{% def format_amount amt %}${{ amt }}{% enddef %}
Sales Report:
{% for item in [{'name': 'Widget', 'amount': 100}, {'name': 'Gadget', 'amount': 50}] %}
- {{ item['name'] }}: {{ format_amount(item['amount']) }}
{% endfor %}
Total: {{ format_amount(150) }}
""".strip()
    
    expected_report = """
Sales Report:

- Widget: $100

- Gadget: $50

Total: $150
""".strip()
    
    test_case(
        simple_report,
        expected_report,
        "Sales report generation"
    )

def test_email_template():
    """Test email template generation"""
    print("\nTesting email template generation...")
    print("=" * 60)
    
    # Email template with personalization
    email_template = """
{% capture user_name %}John Doe{% endcapture %}
{% capture user_email %}john@example.com{% endcapture %}
{% capture order_id %}12345{% endcapture %}
{% capture items %}[{'name': 'Book', 'qty': 2, 'price': 15.99}, {'name': 'Pen', 'qty': 5, 'price': 2.50}]{% endcapture %}

Subject: Order Confirmation #{{ order_id }}

Dear {{ user_name }},

Thank you for your order! Here are the details:

Order #: {{ order_id }}
Email: {{ user_email }}

Items ordered:
{% for item in eval(items) %}
- {{ item['name'] }} (Qty: {{ item['qty'] }}) - ${{ item['price'] * item['qty'] }}
{% endfor %}

{% capture total %}0{% endcapture %}
{% for item in eval(items) %}
{% capture total %}{{ float(total) + (item['price'] * item['qty']) }}{% endcapture %}
{% endfor %}
Total: ${{ total }}

Best regards,
The Store Team
""".strip()
    
    expected_email = """
Subject: Order Confirmation #12345

Dear John Doe,

Thank you for your order! Here are the details:

Order #: 12345
Email: john@example.com

Items ordered:

- Book (Qty: 2) - $31.98

- Pen (Qty: 5) - $12.5


Total: $44.48

Best regards,
The Store Team
""".strip()
    
    test_case(
        email_template,
        expected_email,
        "Email template with order details"
    )

def test_configuration_file_generation():
    """Test configuration file generation"""
    print("\nTesting configuration file generation...")
    print("=" * 60)
    
    # Config file template
    config_template = """
{% capture app_name %}MyApp{% endcapture %}
{% capture version %}1.0.0{% endcapture %}
{% capture debug %}False{% endcapture %}
{% capture features %}['auth', 'api', 'web']{% endcapture %}
{% capture db_config %}{'host': 'localhost', 'port': 5432, 'name': 'myapp_db'}{% endcapture %}

# {{ app_name }} Configuration v{{ version }}
# Generated on {{ '2024-01-01' }}

[app]
name = "{{ app_name }}"
version = "{{ version }}"
debug = {{ debug }}

[features]
{% for feature in eval(features) %}
{{ feature }} = true
{% endfor %}

[database]
{% for key, value in eval(db_config).items() %}
{{ key }} = {{ value if isinstance(value, int) else '"' + str(value) + '"' }}
{% endfor %}
""".strip()
    
    expected_config = """
# MyApp Configuration v1.0.0
# Generated on 2024-01-01

[app]
name = "MyApp"
version = "1.0.0"
debug = False

[features]

auth = true

api = true

web = true


[database]

host = "localhost"

port = 5432

name = "myapp_db"
""".strip()
    
    test_case(
        config_template,
        expected_config,
        "Configuration file generation"
    )

def test_markdown_documentation():
    """Test Markdown documentation generation"""
    print("\nTesting Markdown documentation generation...")
    print("=" * 60)
    
    # API documentation template
    api_doc_template = """
{% capture api_name %}User API{% endcapture %}
{% capture endpoints %}[
  {'method': 'GET', 'path': '/users', 'desc': 'List all users'},
  {'method': 'GET', 'path': '/users/{id}', 'desc': 'Get user by ID'},
  {'method': 'POST', 'path': '/users', 'desc': 'Create new user'}
]{% endcapture %}

# {{ api_name }}

This document describes the available API endpoints.

## Endpoints

{% for endpoint in eval(endpoints) %}
### {{ endpoint['method'] }} {{ endpoint['path'] }}

{{ endpoint['desc'] }}

{% endfor %}

## Usage Examples

```bash
# List users
curl -X GET /users

# Get specific user
curl -X GET /users/123
```
""".strip()
    
    expected_doc = """
# User API

This document describes the available API endpoints.

## Endpoints


### GET /users

List all users


### GET /users/{id}

Get user by ID


### POST /users

Create new user


## Usage Examples

```bash
# List users
curl -X GET /users

# Get specific user
curl -X GET /users/123
```
""".strip()
    
    test_case(
        api_doc_template,
        expected_doc,
        "Markdown API documentation"
    )

def test_complex_data_processing():
    """Test complex data processing scenarios"""
    print("\nTesting complex data processing...")
    print("=" * 60)
    
    # Data transformation template
    data_template = """
{% capture raw_data %}[
  {'name': 'Alice', 'age': 30, 'department': 'Engineering'},
  {'name': 'Bob', 'age': 25, 'department': 'Marketing'},
  {'name': 'Charlie', 'age': 35, 'department': 'Engineering'},
  {'name': 'Diana', 'age': 28, 'department': 'Sales'}
]{% endcapture %}

{% def filter_by_dept data dept %}{% for person in data %}{% if person['department'] == dept %}{{ person['name'] }}:{{ person['age'] }};{% endif %}{% endfor %}{% enddef %}

{% def get_avg_age data %}{{ sum(person['age'] for person in data) / len(data) }}{% enddef %}

Employee Summary Report
======================

Engineering Team:
{{ filter_by_dept(eval(raw_data), 'Engineering') }}

Marketing Team:
{{ filter_by_dept(eval(raw_data), 'Marketing') }}

Sales Team:
{{ filter_by_dept(eval(raw_data), 'Sales') }}

Average Age: {{ get_avg_age(eval(raw_data)) }}
""".strip()
    
    expected_summary = """
Employee Summary Report
======================

Engineering Team:
Alice:30;Charlie:35;

Marketing Team:
Bob:25;

Sales Team:
Diana:28;

Average Age: 29.5
""".strip()
    
    test_case(
        data_template,
        expected_summary,
        "Complex data processing with functions"
    )

def test_conditional_layout():
    """Test conditional layout scenarios"""
    print("\nTesting conditional layout scenarios...")
    print("=" * 60)
    
    # Responsive layout template
    layout_template = """
{% capture device %}mobile{% endcapture %}
{% capture user_type %}premium{% endcapture %}
{% capture show_ads %}{{ 'false' if user_type == 'premium' else 'true' }}{% endcapture %}

<!DOCTYPE html>
<html>
<head>
{% if device == 'mobile' %}
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="mobile.css">
{% else %}
    <link rel="stylesheet" href="desktop.css">
{% endif %}
</head>
<body>
    <div class="{% if device == 'mobile' %}mobile-layout{% else %}desktop-layout{% endif %}">
        <header>Welcome!</header>
        
        {% if user_type == 'premium' %}
        <div class="premium-banner">Premium User Benefits</div>
        {% endif %}
        
        <main>Content goes here</main>
        
        {% if eval(show_ads) %}
        <aside class="ads">Advertisement</aside>
        {% endif %}
    </div>
</body>
</html>
""".strip()
    
    expected_layout = """
<!DOCTYPE html>
<html>
<head>

    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="mobile.css">

</head>
<body>
    <div class="mobile-layout">
        <header>Welcome!</header>
        
        
        <div class="premium-banner">Premium User Benefits</div>
        
        
        <main>Content goes here</main>
        
        
    </div>
</body>
</html>
""".strip()
    
    test_case(
        layout_template,
        expected_layout,
        "Conditional responsive layout"
    )

def test_iterative_processing():
    """Test iterative processing scenarios"""
    print("\nTesting iterative processing...")
    print("=" * 60)
    
    # Batch processing template
    batch_template = """
{% capture batch_size %}3{% endcapture %}
{% capture items %}['item1', 'item2', 'item3', 'item4', 'item5', 'item6', 'item7']{% endcapture %}

{% def process_batch batch_items %}
Batch Processing:
{% for item in batch_items %}
  Processing {{ item }}... ✓
{% endfor %}
Batch Complete!

{% enddef %}

{% capture all_items %}{{ eval(items) }}{% endcapture %}
{% capture current_batch %}[]{% endcapture %}
{% capture batch_count %}0{% endcapture %}

{% for item in eval(items) %}
{% capture current_batch %}{{ eval(current_batch) + [item] }}{% endcapture %}
{% if len(eval(current_batch)) == int(batch_size) %}
{{ process_batch(eval(current_batch)) }}
{% capture current_batch %}[]{% endcapture %}
{% capture batch_count %}{{ int(batch_count) + 1 }}{% endcapture %}
{% endif %}
{% endfor %}

{% if eval(current_batch) %}
{{ process_batch(eval(current_batch)) }}
{% capture batch_count %}{{ int(batch_count) + 1 }}{% endcapture %}
{% endif %}

Total batches processed: {{ batch_count }}
""".strip()
    
    expected_batch = """
Batch Processing:

  Processing item1... ✓

  Processing item2... ✓

  Processing item3... ✓

Batch Complete!


Batch Processing:

  Processing item4... ✓

  Processing item5... ✓

  Processing item6... ✓

Batch Complete!


Batch Processing:

  Processing item7... ✓

Batch Complete!


Total batches processed: 3
""".strip()
    
    test_case(
        batch_template,
        expected_batch,
        "Iterative batch processing"
    )

def test_state_machine():
    """Test state machine simulation"""
    print("\nTesting state machine simulation...")
    print("=" * 60)
    
    # Simple state machine
    state_template = """
{% capture current_state %}start{% endcapture %}
{% capture events %}['begin', 'process', 'complete', 'reset']{% endcapture %}

State Machine Simulation:
=========================

{% for event in eval(events) %}
Current State: {{ current_state }}
Event: {{ event }}

{% if current_state == 'start' and event == 'begin' %}
{% capture current_state %}processing{% endcapture %}
→ Transitioning to processing
{% elif current_state == 'processing' and event == 'process' %}
{% capture current_state %}processing{% endcapture %}
→ Continuing processing
{% elif current_state == 'processing' and event == 'complete' %}
{% capture current_state %}finished{% endcapture %}
→ Processing complete
{% elif event == 'reset' %}
{% capture current_state %}start{% endcapture %}
→ Resetting to start
{% else %}
→ Invalid transition ignored
{% endif %}

New State: {{ current_state }}
---

{% endfor %}

Final State: {{ current_state }}
""".strip()
    
    expected_state = """
State Machine Simulation:
=========================


Current State: start
Event: begin


→ Transitioning to processing

New State: processing
---


Current State: processing
Event: process


→ Continuing processing

New State: processing
---


Current State: processing
Event: complete


→ Processing complete

New State: finished
---


Current State: finished
Event: reset


→ Resetting to start

New State: start
---


Final State: start
""".strip()
    
    test_case(
        state_template,
        expected_state,
        "State machine simulation"
    )

def main():
    """Run all integration scenario tests"""
    print("🧪 Integration Scenarios Test Suite")
    print("=" * 60)
    
    test_web_page_template()
    test_data_report_generation()
    test_email_template()
    test_configuration_file_generation()
    test_markdown_documentation()
    test_complex_data_processing()
    test_conditional_layout()
    test_iterative_processing()
    test_state_machine()
    
    print("\n" + "=" * 60)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All integration scenario tests passed!")
        return 0
    else:
        print(f"❌ {total - passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 