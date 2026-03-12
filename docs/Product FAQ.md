# Meridian Analytics Platform — Frequently Asked Questions

## General

### What is Meridian Analytics Platform?

Meridian Analytics Platform (MAP) is a cloud-based business intelligence and data analytics solution that helps organizations transform raw data into actionable insights. MAP supports real-time dashboards, automated reporting, predictive analytics, and collaborative data exploration across teams.

### Who is MAP designed for?

MAP serves data analysts, business intelligence teams, product managers, and executives across industries including finance, healthcare, retail, and SaaS. No coding experience is required for basic dashboard creation, though advanced users can leverage our SQL editor and Python integration.

### What data sources does MAP support?

MAP connects to over 50 data sources including PostgreSQL, MySQL, Snowflake, BigQuery, Redshift, MongoDB, Salesforce, HubSpot, Google Analytics, Shopify, and flat files (CSV, Excel, JSON). Custom API connectors are available on the Enterprise plan.

### Is there a free trial?

Yes. All new accounts receive a 14-day free trial of the Professional plan with full access to all features. No credit card is required to start. At the end of the trial, you can choose a paid plan or downgrade to the free Starter plan (limited to 3 dashboards and 1 data source).

## Pricing

### What plans are available?

- **Starter (Free)**: 3 dashboards, 1 data source, 1 user, 100MB storage
- **Professional ($49/user/month)**: Unlimited dashboards, 10 data sources, scheduled reports, email alerts
- **Team ($89/user/month)**: Everything in Professional plus collaboration features, shared workspaces, role-based access, API access
- **Enterprise (custom pricing)**: SSO/SAML, dedicated support, custom connectors, SLA guarantees, on-premises deployment option

### Is there a discount for annual billing?

Yes. Annual billing saves 20% compared to monthly billing. For example, the Professional plan is $39/user/month when billed annually instead of $49/user/month.

### Can I switch plans at any time?

Upgrades take effect immediately and are prorated. Downgrades take effect at the start of the next billing cycle. Contact support@meridiantech.com to change plans.

## Features

### How do I create a dashboard?

Click "New Dashboard" from the home screen, choose a data source, and drag-and-drop visualization widgets onto the canvas. MAP supports 25+ chart types including bar, line, pie, scatter, heatmap, funnel, and geographic maps. Each widget can be configured with filters, date ranges, and drill-down capabilities.

### Can I schedule automated reports?

Yes, on Professional plans and above. Navigate to any dashboard, click "Schedule," and configure delivery frequency (daily, weekly, monthly), format (PDF, CSV, or inline email), and recipients. Reports are sent at the specified time in your account's timezone.

### Does MAP support real-time data?

MAP supports near-real-time data with refresh intervals as low as 1 minute for supported data sources (Snowflake, BigQuery, PostgreSQL). Live streaming dashboards with sub-second updates are available on the Enterprise plan.

### Can I embed dashboards in my own application?

Yes. Team and Enterprise plans include an embedding SDK that lets you embed interactive dashboards into your web application via iframe or JavaScript SDK. Embedded dashboards support theming to match your brand, and user-level row-level security for multi-tenant applications.

### What visualization types are available?

MAP includes 28 visualization types: bar chart, stacked bar, grouped bar, line chart, area chart, pie chart, donut chart, scatter plot, bubble chart, heatmap, treemap, funnel chart, waterfall chart, gauge, KPI card, table, pivot table, geographic map, choropleth map, Sankey diagram, box plot, histogram, radar chart, candlestick chart, Gantt chart, timeline, word cloud, and custom SVG.

### Does MAP support SQL queries?

Yes. The built-in SQL editor supports standard SQL with auto-complete, syntax highlighting, and query history. You can save queries as reusable datasets and use them across multiple dashboards. Team and Enterprise plans support parameterized queries for dynamic filtering.

## Security and Compliance

### How is my data secured?

All data is encrypted in transit (TLS 1.3) and at rest (AES-256). MAP runs on AWS infrastructure with SOC 2 Type II certification. We perform annual third-party penetration testing and maintain a bug bounty program.

### Is MAP HIPAA compliant?

Yes. Enterprise plans include a Business Associate Agreement (BAA) for HIPAA compliance. Contact our sales team at enterprise@meridiantech.com for details.

### Does MAP support Single Sign-On?

SAML-based SSO is available on the Enterprise plan. We support integration with Okta, Azure AD, Google Workspace, and OneLogin. SCIM provisioning for automated user management is also available.

### Where is data stored?

MAP offers data residency in three regions: US (us-east-1, AWS Virginia), EU (eu-west-1, AWS Ireland), and APAC (ap-southeast-1, AWS Singapore). Enterprise customers can specify their preferred region during onboarding.

## Support

### How do I contact support?

- **Starter**: Community forum and documentation only
- **Professional**: Email support with 24-hour response time (business days)
- **Team**: Email and chat support with 8-hour response time (business days)
- **Enterprise**: Dedicated account manager, phone support, 4-hour response time (24/7), and quarterly business reviews

### Where can I find documentation?

Visit docs.meridiantech.com for comprehensive guides, tutorials, API references, and video walkthroughs. The documentation is searchable and organized by topic, feature, and skill level.

### Do you offer training?

Yes. We offer free monthly webinars covering platform basics, advanced analytics, and new features. Enterprise customers receive customized onboarding training sessions (up to 3 sessions included). Additional training packages are available starting at $500/session.
