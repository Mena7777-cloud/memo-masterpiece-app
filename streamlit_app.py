import streamlit as st
from sqlalchemy import or_
from database import SessionLocal, Product, create_db
from datetime import datetime

# --- 1. الإعدادات الأولية والشكل الجمالي ---
st.set_page_config(page_title="نظام إدارة المخزون الفاخر", page_icon="💎", layout="wide")

# تطبيق الـ Theme الجمالي
st.markdown("""
<style>
    /* تغيير لون الخلفية الرئيسي */
    .main {
        background-color: #f0f2f6;
    }
    /* تصميم الكروت (Cards) */
    .st-emotion-cache-1r6slb0 {
        border-radius: 15px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    /* تصميم الأزرار */
    .stButton>button {
        border-radius: 20px;
        border: 1px solid #4CAF50;
        background-color: #4CAF50;
        color: white;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: white;
        color: #4CAF50;
    }
</style>
""", unsafe_allow_html=True)

# إنشاء قاعدة البيانات عند أول تشغيل
create_db()
db = SessionLocal()

# --- 2. الواجهة الرئيسية (العنوان والأقسام) ---
st.title("💎 نظام إدارة المخزون الفاخر")
st.write("تم التصميم والتطوير بواسطة: حنان")
st.markdown("---")

# استخدام Tabs لتنظيم الواجهة بشكل احترافي
tab1, tab2, tab3 = st.tabs(["📊 لوحة التحكم", "📦 إدارة المنتجات", "🔔 التنبيهات"])

# --- القسم الأول: لوحة التحكم ---
with tab1:
    st.header("📊 نظرة عامة على المخزون")
        
    total_products = db.query(Product).count()
    total_quantity = sum([p.quantity for p in db.query(Product).all()])
    total_value = sum([p.price * p.quantity for p in db.query(Product).all()])

    col1, col2, col3 = st.columns(3)
    col1.metric("إجمالي أنواع المنتجات", f"{total_products} نوع")
    col2.metric("إجمالي عدد القطع", f"{total_quantity} قطعة")
    col3.metric("القيمة الإجمالية للمخزون", f"{total_value:,} جنيه")

# --- القسم الثاني: إدارة المنتجات (إضافة، تعديل، عرض، بحث، حذف) ---
with tab2:
    col1, col2 = st.columns([1, 2])

    # العمود الأول: فورم الإضافة والتعديل
    with col1:
        st.header("➕ إضافة / تعديل منتج")
            
        products_list = db.query(Product).order_by(Product.name).all()
        selected_product_name = st.selectbox("لتعديل منتج، اختره من هنا:", 
                                             options=[p.name for p in products_list], 
                                             index=None, placeholder="اختر منتجًا لتعديله...")
            
        product_to_edit = None
        if selected_product_name:
            product_to_edit = db.query(Product).filter(Product.name == selected_product_name).first()

        with st.form("product_form", clear_on_submit=True):
            st.subheader("تفاصيل المنتج الدقيقة:")
            name = st.text_input("اسم المنتج*", value=product_to_edit.name if product_to_edit else "")
            description = st.text_area("وصف المنتج", value=product_to_edit.description if product_to_edit else "")
            category = st.text_input("الفئة (المجموعة)", value=product_to_edit.category if product_to_edit else "")
            supplier = st.text_input("المورّد", value=product_to_edit.supplier if product_to_edit else "")
                
            c1, c2 = st.columns(2)
            quantity = c1.number_input("الكمية*", min_value=0, step=1, value=product_to_edit.quantity if product_to_edit else 0)
            price = c2.number_input("السعر (صحيح)*", min_value=0, step=1, value=product_to_edit.price if product_to_edit else 0)
            reorder_level = st.number_input("حد إعادة الطلب (للتنبيهات)", min_value=0, step=1, value=product_to_edit.reorder_level if product_to_edit else 5)

            submitted = st.form_submit_button("💾 حفظ البيانات")
            if submitted:
                if not name or price is None or quantity is None:
                    st.error("❌ الرجاء إدخال الحقول الإجبارية (*)")
                else:
                    if product_to_edit: # تعديل
                        product_to_edit.name, product_to_edit.description, product_to_edit.category, product_to_edit.supplier, product_to_edit.quantity, product_to_edit.price, product_to_edit.reorder_level = name, description, category, supplier, quantity, price, reorder_level
                        st.success(f"✅ تم تعديل المنتج '{name}' بنجاح!")
                    else: # إضافة
                        db.add(Product(name=name, description=description, category=category, supplier=supplier, quantity=quantity, price=price, reorder_level=reorder_level))
                        st.success(f"🎉 تم إضافة المنتج '{name}' بنجاح!")
                    db.commit()
                    st.rerun()

    # العمود الثاني: عرض المنتجات والبحث
    with col2:
        st.header("📋 قائمة المنتجات في المخزون")
        search_term = st.text_input("🔍 ابحث بالاسم، الفئة، أو المورّد...")
            
        query = db.query(Product)
        if search_term:
            search_filter = f"%{search_term}%"
            query = query.filter(or_(Product.name.ilike(search_filter), Product.category.ilike(search_filter), Product.supplier.ilike(search_filter)))
            
        all_products = query.order_by(Product.id.desc()).all()

        if not all_products:
            st.info("ℹ️ لا توجد منتجات لعرضها.")
        else:
            for p in all_products:
                with st.expander(f"**{p.name}** (الكمية: {p.quantity})"):
                    st.write(f"**الوصف:** {p.description or 'لا يوجد'}")
                    st.write(f"**الفئة:** {p.category or 'لا يوجد'}")
                    st.write(f"**المورّد:** {p.supplier or 'لا يوجد'}")
                    st.write(f"**السعر:** {p.price} جنيه")
                    st.write(f"**حد إعادة الطلب:** {p.reorder_level}")
                    st.write(f"**زمن الإضافة:** {p.added_at.strftime('%Y-%m-%d %H:%M')}")
                        
                    if st.button("🗑️ حذف المنتج", key=f"del_{p.id}"):
                        db.delete(p)
                        db.commit()
                        st.rerun()

# --- القسم الثالث: التنبيهات ---
with tab3:
    st.header("🔔 تنبيهات المنتجات التي وصلت لحد إعادة الطلب")
    low_stock_products = db.query(Product).filter(Product.quantity <= Product.reorder_level).all()

    if not low_stock_products:
        st.success("✅ كل المنتجات كميتها ممتازة فوق حد إعادة الطلب.")
    else:
        st.warning(f"⚠️ يوجد {len(low_stock_products)} منتج بحاجة لإعادة التزويد:")
        for p in low_stock_products:
            st.error(f"**{p.name}** - الكمية الحالية: **{p.quantity}** (حد إعادة الطلب: {p.reorder_level})")

db.close()
