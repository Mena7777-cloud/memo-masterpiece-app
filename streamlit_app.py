import streamlit as st
from sqlalchemy import or_
from database import SessionLocal, Product, User, create_db_and_users, verify_password
from streamlit_option_menu import option_menu
import pandas as pd
from io import BytesIO

# --- 1. الإعدادات الأولية والشكل الجمالي الفائق ---
st.set_page_config(page_title="نظام إدارة التخزين الذكي", page_icon="🧠", layout="wide")

# تطبيق الـ Theme الجمالي الفاخر
st.markdown("""
<style>
    /* الخلفية العامة */
    .main { background-color: #F0F2F6; }

    /* تصميم الكروت الأنيقة */
    .card {
        background-color: white;
        border-radius: 15px;
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    .card:hover {
        transform: translateY(-5px);
    }
        
    /* تصميم العنوان الرئيسي */
    h1 {
        color: #1A237E; /* أزرق داكن */
        text-align: center;
        font-family: 'Arial', sans-serif;
    }
</style>
""", unsafe_allow_html=True)

# إنشاء قاعدة البيانات والمستخدمين
create_db_and_users()
db = SessionLocal()

# --- 2. نظام تسجيل الدخول الاحترافي ---
if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    st.title("🧠 نظام إدارة التخزين الذكي")
    st.markdown("<br>", unsafe_allow_html=True)
        
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        with st.container():
            st.header("🔐 تسجيل الدخول")
            with st.form("login_form"):
                username = st.text_input("👤 اسم المستخدم")
                password = st.text_input("🔑 كلمة المرور", type="password")
                submitted = st.form_submit_button("➡️ تسجيل الدخول")
                    
                if submitted:
                    user_in_db = db.query(User).filter(User.username == username).first()
                    if user_in_db and verify_password(password, user_in_db.password_hash):
                        st.session_state.user = user_in_db
                        st.rerun()
                    else:
                        st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 3. الواجهة الرئيسية بعد تسجيل الدخول ---
with st.sidebar:
    st.title(f"مرحباً, {st.session_state.user.username.capitalize()}")
    st.write(f"**الصلاحيات:** {'👑 مدير' if st.session_state.user.role == 'admin' else '👤 مستخدم'}")
        
    selected_tab = option_menu(
        menu_title="القائمة الرئيسية",
        options=["📊 لوحة التحكم", "🗃️ إدارة التخزين", "🔔 التنبيهات"],
        icons=["bar-chart-line-fill", "box-seam-fill", "bell-fill"],
        menu_icon="list-task", default_index=0,
    )
        
    st.markdown("---")
    if st.button("🚪 تسجيل الخروج"):
        st.session_state.user = None
        st.rerun()

# --- عرض المحتوى بناءً على الاختيار ---

if selected_tab == "📊 لوحة التحكم":
    st.header("📊 لوحة التحكم")
    total_products = db.query(Product).count()
    total_quantity = sum([p.quantity for p in db.query(Product).all()]) or 0
    total_value = sum([p.price * p.quantity for p in db.query(Product).all()]) or 0
    col1, col2, col3 = st.columns(3)
    col1.metric("إجمالي أنواع المنتجات", f"{total_products} نوع")
    col2.metric("إجمالي عدد القطع", f"{total_quantity} قطعة")
    col3.metric("القيمة الإجمالية للتخزين", f"{total_value:,} جنيه")

    # إضافة احترافية: تصدير البيانات لملف Excel
    st.markdown("---")
    st.subheader("📥 تصدير البيانات")
    all_products_df = pd.read_sql(db.query(Product).statement, db.bind)
        
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        all_products_df.to_excel(writer, index=False, sheet_name='Products')
        
    st.download_button(
        label="📄 تنزيل كملف Excel",
        data=output.getvalue(),
        file_name="storage_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

elif selected_tab == "🗃️ إدارة التخزين":
    st.header("🗃️ إدارة التخزين")
        
    # فورم الإضافة فقط للمدير
    if st.session_state.user.role == 'admin':
        with st.expander("➕ لإضافة منتج جديد، اضغط هنا", expanded=False):
            with st.form("add_form", clear_on_submit=True):
                name = st.text_input("اسم المنتج*")
                description = st.text_area("وصف المنتج")
                category = st.text_input("الفئة (المجموعة)")
                supplier = st.text_input("المورّد")
                c1, c2 = st.columns(2)
                quantity = c1.number_input("الكمية*", min_value=0, step=1)
                price = c2.number_input("السعر (صحيح)*", min_value=0, step=1)
                reorder_level = st.number_input("حد إعادة الطلب (للتنبيهات)", min_value=0, step=1, value=5)
                    
                submitted = st.form_submit_button("💾 إضافة المنتج")
                if submitted and name:
                    db.add(Product(name=name, description=description, category=category, supplier=supplier, quantity=quantity, price=price, reorder_level=reorder_level))
                    db.commit()
                    st.success("🎉 تم إضافة المنتج بنجاح!")
                    st.rerun()

    # عرض وتعديل وحذف المنتجات
    search_term = st.text_input("🔍 ابحث بالاسم، الفئة، أو المورّد...")
    query = db.query(Product)
    if search_term:
        search_filter = f"%{search_term}%"
        query = query.filter(or_(Product.name.ilike(search_filter), Product.category.ilike(search_filter), Product.supplier.ilike(search_filter)))
        
    all_products = query.order_by(Product.id.desc()).all()
    for p in all_products:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        with st.container():
            st.subheader(f"🏷️ {p.name}")
            c1, c2, c3 = st.columns(3)
            c1.info(f"**الكمية:** {p.quantity}")
            c2.success(f"**السعر:** {p.price} جنيه")
            c3.warning(f"**حد إعادة الطلب:** {p.reorder_level}")
                
            with st.expander("تفاصيل إضافية 📝"):
                st.write(f"**الوصف:** {p.description or 'لا يوجد'}")
                st.write(f"**الفئة:** {p.category or 'لا يوجد'}")
                st.write(f"**المورّد:** {p.supplier or 'لا يوجد'}")
                st.write(f"**زمن الإضافة:** {p.added_at.strftime('%Y-%m-%d %H:%M')}")
                
            # أزرار التعديل والحذف فقط للمدير
            if st.session_state.user.role == 'admin':
                c1, c2 = st.columns([1, 5])
                with c1:
                    if st.button("🗑️ حذف", key=f"del_{p.id}"):
                        # هنا يمكن إضافة رسالة تأكيد
                        db.delete(p)
                        db.commit()
                        st.rerun()
                # (يمكن إضافة زر التعديل هنا بنفس الطريقة)
        st.markdown('</div>', unsafe_allow_html=True)

elif selected_tab == "🔔 التنبيهات":
    st.header("🔔 تنبيهات المنتجات")
    low_stock_products = db.query(Product).filter(Product.quantity <= Product.reorder_level).all()
    if not low_stock_products:
        st.success("✅ كل المنتجات كميتها ممتازة فوق حد إعادة الطلب.")
    else:
        st.warning(f"⚠️ يوجد {len(low_stock_products)} منتج بحاجة لإعادة التزويد:")
        for p in low_stock_products:
            st.error(f"**{p.name}** - الكمية الحالية: **{p.quantity}** (حد إعادة الطلب: {p.reorder_level})")

db.close()
