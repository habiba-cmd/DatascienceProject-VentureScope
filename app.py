"""VentureScope — entrepreneur-facing dashboard, preserving research evidence gates."""
import json
from pathlib import Path
import pandas as pd
import streamlit as st
from src.assessment import sample_assessment, readiness, recommendations, sensitivity
from src.concept import match_categories, competitor_profile, evidence_report

st.set_page_config(page_title='VentureScope • Business Intelligence', page_icon='🧭', layout='wide', initial_sidebar_state='expanded')
st.markdown('''<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html,body,[class*="css"], [data-testid="stApp"] {font-family:Inter,Arial,sans-serif;}
[data-testid="stAppViewContainer"] {background:linear-gradient(135deg,#f6f8fc 0%,#eef3fa 100%);}
[data-testid="stSidebar"] {background:#101e37;}
[data-testid="stSidebar"] * {color:#f0f5ff!important;}
[data-testid="stSidebar"] input {color:#15243c!important;}
[data-testid="stSidebar"] [data-baseweb="select"] * {color:#15243c!important;}
h1,h2,h3 {color:#142b4d;letter-spacing:-.035em;}
h1 {font-weight:800!important;}
[data-testid="stMetric"] {background:white;border:1px solid #e2eaf5;border-radius:16px;padding:17px;box-shadow:0 5px 16px rgba(26,47,87,.045);}
[data-testid="stMetricLabel"] {color:#667891;}
[data-testid="stMetricValue"] {color:#132b4f;font-weight:750;}
.hero {background:linear-gradient(105deg,#122b52,#2357a5);padding:30px 34px;border-radius:20px;color:white;margin-bottom:22px;box-shadow:0 12px 30px #173b6d1f;}
.hero h1 {color:white!important;font-size:2.25rem;margin:0 0 8px;}
.hero p {color:#dce9fc;font-size:1rem;margin:0;}
.pill {display:inline-block;background:#dfeafa;color:#19447c;border-radius:20px;padding:6px 12px;font-size:.82rem;font-weight:700;}
.section-note {color:#61748f;font-size:.9rem;}
[data-testid="stTabs"] [role="tab"] {font-weight:650;}
</style>''', unsafe_allow_html=True)

BASE=Path(__file__).resolve().parent
OUT=BASE/'outputs'
IND=OUT/'amazon_category_indicators.csv'
if not IND.exists():
    st.error('Processed category indicators are missing. Run VentureScope_Complete.ipynb and check the outputs folder.')
    st.code(str(IND));st.stop()

@st.cache_data(show_spinner=False)
def read_csv(path):
    return pd.read_csv(path)

a=read_csv(IND)
if 'category' not in a.columns:
    st.error('The category indicators file has no category column.');st.stop()
categories=sorted(a['category'].dropna().astype(str).unique().tolist())

with st.sidebar:
    st.markdown('## 🧭 VentureScope')
    st.caption('Business opportunity intelligence')
    st.divider()
    st.markdown('### 1 · Your business idea')
    idea=st.text_input('What would you like to launch?',value='Affordable durable suitcases',help='Describe the product or service in plain language.')
    region=st.text_input('Where will you sell?',value='Pakistan',help='This identifies your intended market; the dataset is not a Pakistan market survey.')
    target=st.text_input('Who are your customers?',value='Budget-conscious travelers')
    st.markdown('### 2 · Choose a relevant category')
    try:
        suggestions=match_categories(idea,categories,top_k=6)
        candidates=suggestions['category'].tolist()
    except Exception:
        candidates=[]
    keywords=['suitcase','luggage','travel','bag']
    recommended=next((c for c in categories if any(k in c.lower() for k in keywords) and any(k in idea.lower() for k in keywords)),None)
    if recommended is None and candidates:
        recommended=candidates[0]
    if st.session_state.get('last_idea') != idea:
        st.session_state['last_idea'] = idea
        st.session_state['selected_category'] = recommended if recommended in categories else categories[0]
    if 'selected_category' not in st.session_state:
        st.session_state.selected_category=recommended if recommended in categories else categories[0]
    if st.session_state.selected_category not in categories:
        st.session_state.selected_category=categories[0]
    category=st.selectbox('Product evidence category',categories,key='selected_category',help='Confirm this category manually. Matching is only a suggestion.')
    if recommended and category!=recommended:
        st.caption('Suggested for this idea: '+recommended)
    st.divider()
    with st.expander('Founder readiness · optional',expanded=False):
        budget=st.slider('Budget preparation',0,100,30)
        team=st.slider('Team preparation',0,100,30)
        prototype=st.checkbox('Working prototype available')
        early=st.checkbox('Early customers or buyers')
    st.caption('Research prototype · Not a business-success prediction')

founder={'budget_readiness':budget/100,'team_readiness':team/100,'prototype':prototype,'early_users':early}
row=a[a.category.astype(str)==category].iloc[0]

def fmt(x,kind='number'):
    try:
        if pd.isna(x):return 'Not available'
        x=float(x)
        if kind=='money':return '${:,.2f}'.format(x)
        if kind=='rating':return '{:.2f} / 5'.format(x)
        return '{:,.0f}'.format(x)
    except (TypeError,ValueError):return 'Not available'

st.markdown('<div class="hero"><h1>VentureScope</h1><p>From business idea to evidence-informed decisions · A clearer view of your next opportunity</p></div>',unsafe_allow_html=True)
st.markdown('**YOUR OPPORTUNITY**')
st.title(idea.strip() or 'Untitled business idea')
st.caption(f'📍 Target market: {region or "Not specified"}   ·   👥 Customers: {target or "Not specified"}   ·   🧳 Evidence category: {category}')

# Preserve the research engine's original evidence gate; no fabricated values.
with st.expander('Add independently supported evidence (optional)',expanded=False):
    st.caption('Leave unknown dimensions blank. These are research inputs, not automatic scores.')
    cp=st.number_input('Human-validated customer-problem score (0–100)',min_value=0,max_value=100,value=None,placeholder='Not available')
    fit=st.number_input('Evidence-backed product–problem fit (0–100)',min_value=0,max_value=100,value=None,placeholder='Not available')
    access=st.number_input('Verified market accessibility (0–100)',min_value=0,max_value=100,value=None,placeholder='Not available')
assessment=sample_assessment(row,cp,fit,access)
founder_score=readiness(founder)
rec=recommendations(assessment,founder)

m1,m2,m3,m4=st.columns(4)
m1.metric('Products in sample',fmt(row.get('products')))
m2.metric('Median listed price',fmt(row.get('median_price'),'money'))
m3.metric('Average product rating',fmt(row.get('mean_rating'),'rating'))
m4.metric('Evidence coverage',f"{assessment['coverage']*100:.0f}%")
st.caption('Product statistics are from a sampled Amazon catalog, not a full census or a current forecast for your selected country.')

overview,market,assessment_tab,advice,research=st.tabs(['🏠 Overview','📊 Market & competition','🎯 Opportunity assessment','💡 Action plan','🔬 Research evidence'])

with overview:
    st.subheader('Your business opportunity at a glance')
    l,r=st.columns([1.25,1])
    with l:
        with st.container(border=True):
            st.markdown('#### Market opportunity status')
            if assessment['score'] is None:
                st.warning('Insufficient verified evidence for a final opportunity grade')
                st.write('The system has usable category-level signals, but a defensible overall grade also requires verified customer needs, product fit and market accessibility.')
            else:
                st.success(f"{assessment['score']:.1f}/100 · {assessment['category']}")
            st.progress(float(assessment['coverage']))
            st.caption(f"{assessment['coverage']*100:.0f}% weighted evidence coverage · Missing inputs are not assigned artificial scores")
    with r:
        with st.container(border=True):
            st.markdown('#### Founder readiness')
            st.metric('Founder preparation index',f'{founder_score:.0f}/100')
            st.caption('Self-reported readiness. It never changes the market opportunity score.')
            st.progress(founder_score/100)
    st.subheader('What should you do next?')
    st.markdown('**1. Confirm your product category** · **2. Examine comparable products** · **3. Validate real customer problems** · **4. Test demand in your target region**')
    st.info('You can explore the available product evidence now. An unsupported grade is intentionally withheld.')
    st.markdown('#### Target-market validation plan')
    st.write(f'For **{region.strip() or "your chosen region"}**, validate customer willingness to pay, local competitors, shipping/import costs, regulations and distribution channels before treating the opportunity as locally viable.')
    st.caption('Changing the region changes the market-specific validation brief; it does not fabricate local demand statistics.')

with market:
    st.subheader('Market & competitor intelligence')
    st.caption('Historical/sampled product signals; useful for exploration, not proof of local market demand.')
    c1,c2=st.columns(2)
    with c1:
        st.markdown('#### Category signals')
        values={
            'Products in sample':row.get('products'),
            'Mean product rating':row.get('mean_rating'),
            'Last-month purchase proxy (sample sum)':row.get('bought_last_month_sum'),
        }
        st.dataframe(pd.DataFrame([{'Indicator':k,'Observed value':v} for k,v in values.items()]),hide_index=True,use_container_width=True)
    with c2:
        st.markdown('#### Price and competition interpretation')
        st.write(f"The selected **{category}** category has a sampled median listed price of **{fmt(row.get('median_price'),'money')}**.")
        st.write('This can help frame a preliminary pricing comparison, but cannot establish profitability, local affordability or market size.')
    pth=OUT/'amazon_products_sample_with_categories.csv'
    if pth.exists():
        try:
            products=read_csv(pth)
            profile,leaders=competitor_profile(products,category)
            st.markdown('#### Comparable products')
            if not leaders.empty:
                st.dataframe(leaders,hide_index=True,use_container_width=True)
                if 'price' in leaders.columns:
                    prices=pd.to_numeric(leaders['price'],errors='coerce').dropna()
                    if not prices.empty:
                        st.markdown('#### Listed price distribution · top sampled products')
                        st.bar_chart(prices.reset_index(drop=True))
            else:st.info('No individual competitor rows available for this selected category.')
        except Exception as exc:
            st.warning(f'Competitor details unavailable: {exc}')
    else:st.info('Detailed competitor rows are unavailable. The summary indicators above are still usable.')

with assessment_tab:
    st.subheader('Five-dimension opportunity assessment')
    st.caption('The research rubric weights demand 25%, customer problems 25%, competition 20%, product fit 20%, and accessibility 10%.')
    names={'market_demand':'Market demand','customer_problem':'Customer problems','competition':'Competition','product_fit':'Product–problem fit','accessibility':'Market accessibility'}
    weights={'market_demand':25,'customer_problem':25,'competition':20,'product_fit':20,'accessibility':10}
    records=[]
    for k,label in names.items():
        value=assessment['dimensions'].get(k)
        records.append({'Dimension':label,'Weight':f'{weights[k]}%','Score':round(float(value),1) if value is not None else 'Not available','Evidence status':'Available proxy / supplied evidence' if value is not None else 'Missing'})
    st.dataframe(pd.DataFrame(records),hide_index=True,use_container_width=True)
    if assessment['score'] is None:
        st.warning('No final grade: one or more essential dimensions lack verified evidence.')
    else:
        st.metric('Weighted rubric result',f"{assessment['score']:.1f}/100")
        st.success(assessment['category'])
    chart={names[k]:v for k,v in assessment['dimensions'].items() if v is not None}
    if chart:st.bar_chart(pd.Series(chart))
    st.markdown('#### Evidence needed for a complete assessment')
    for k,label in names.items():
        if assessment['dimensions'].get(k) is None:
            st.write('○ '+label+' — independent, category- and market-matched validation required')
    st.caption('Sample-derived demand/competition scores are exploratory proxies. Founder readiness is not included in the weighted market score.')

with advice:
    st.subheader('Recommended next actions')
    st.markdown(f'**Region-specific research priorities — {region.strip() or "market not yet specified"}**')
    st.write('Interview target customers in the selected market; record competitor prices in local currency; confirm delivery costs, taxes and relevant regulations; test a small paid campaign or pre-order before scaling.')
    if rec.empty:
        st.info('No rule-based recommendations were triggered by the available inputs.')
    else:
        for _,item in rec.iterrows():
            with st.container(border=True):
                st.markdown('**'+str(item.get('dimension','Recommendation')).replace('_',' ').title()+'**')
                st.write(item['recommendation'])
                st.caption('Rule: '+str(item.get('rule_id',''))+' · Evidence: '+str(item.get('source','')))
    st.subheader('Scenario and robustness')
    st.write('Explore changes to founder readiness using the sidebar. Market evidence remains unchanged by founder inputs.')
    scenario=sensitivity(assessment['dimensions'],assessment['provenance'])
    if scenario.get('status')=='insufficient evidence':
        st.info('Weight-sensitivity results require a complete, evidence-supported market score. No scenario outcome is fabricated.')
    else:st.json(scenario)

with research:
    st.subheader('Evidence provenance & research validation')
    st.markdown('**Data sources:** Amazon Reviews Polarity (sentiment only), Amazon Products (sampled catalog), historical Olist transactions, and historical UCI Online Retail transactions.')
    st.warning('Amazon Reviews Polarity has no product IDs, so its sentiment examples cannot be joined to the Amazon Products catalog. Historical international data cannot establish current demand in '+(region or 'the selected region')+'.')
    ann=OUT/'annotation_status.json'
    if ann.exists():
        try:st.json(json.loads(ann.read_text(encoding='utf-8')))
        except Exception:st.info('Annotation status file cannot be read.')
    else:st.info('Human-labelled customer-need evaluation is pending.')
    st.markdown('#### Candidate category matching (requires human confirmation)')
    if not suggestions.empty:st.dataframe(suggestions,hide_index=True,use_container_width=True)
    st.markdown('#### Research limitations')
    st.write('No validated unmet-need classifier is claimed without human labels; no business success prediction is claimed; geographic transfer and expert validation remain open research tasks.')

st.divider()
st.markdown('### Export your opportunity brief')
report={
    'business_idea':idea,'target_region':region,'target_customers':target,
    'selected_category':category,'product_sample':{
        'products':row.get('products'),'median_price':row.get('median_price'),
        'mean_rating':row.get('mean_rating'),'bought_last_month_sum':row.get('bought_last_month_sum')},
    'assessment':assessment,'founder_readiness_separate':founder_score,
    'recommendations':rec.to_dict('records'),
    'limitations':['Sampled Amazon product data is not a current local market census','Human-validated unmet needs are not established unless separately provided','Founder readiness does not affect market score','A missing score is not replaced with invented values']}
st.download_button('⬇ Download evidence-based assessment (JSON)',json.dumps(report,indent=2,default=str),file_name='VentureScope_Business_Assessment.json',mime='application/json',use_container_width=True)
st.caption('VentureScope · Explainable research prototype · Results are decision-support evidence, not a guarantee of business success.')
