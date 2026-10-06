import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="テントマップの変換", layout="wide")
st.title("テントマップの拡大・縮小・平行移動・反転")
st.markdown(r"""
基本となるテントマップ $f(x)$ は区間 $0 \le x \le 1$ で定義されます。
$$ f(x) = \begin{cases} 2x & (0\leq x\leq 1/2) \\ 2-2x & (1/2 \leq x\leq 1)\\ 0 & (それ以外) \end{cases} $$
この関数に対して、$y = a \cdot f(b(x - p)) + q$ の形で変換を行い、図形がどう変化するかを観察します。
""")

# --- サイドバー：パラメータ設定 ---
st.sidebar.header("変換パラメータ")

st.sidebar.markdown(r"拡大・縮小・反転 ($a, b$)")
a = st.sidebar.slider("縦の倍率 a (マイナスで上下反転)", min_value=-3.0, max_value=3.0, value=1.0, step=0.1)
b = st.sidebar.slider("横の倍率 b (マイナスで左右反転)", min_value=-3.0, max_value=3.0, value=1.0, step=0.1)

st.sidebar.markdown(r"平行移動 ($p, q$)")
p = st.sidebar.slider("横の移動 p (x方向)", min_value=-2.0, max_value=2.0, value=0.0, step=0.2)
q = st.sidebar.slider("縦の移動 q (y方向)", min_value=-2.0, max_value=2.0, value=0.0, step=0.2)

# --- ゼロ割り（b=0）の防止 ---
if b == 0:
    st.sidebar.warning("b=0 だと関数が定義できないため、b=0.1 に補正します。")
    b = 0.1

# --- テントマップの定義 ---
def tent_map(x):
    y = np.full_like(x, np.nan)
    mask1 = (x >= 0) & (x <= 0.5)
    mask2 = (x > 0.5) & (x <= 1)
    y[mask1] = 2 * x[mask1]
    y[mask2] = 2 - 2 * x[mask2]
    return y

def transformed_tent_map(x, a, b, p, q):
    return a * tent_map(b * (x - p)) + q

# --- データ生成 ---
# 端まで途切れないように余裕を持たせた範囲
x = np.linspace(-15, 15, 3000)
y_base = tent_map(x)
y_trans = transformed_tent_map(x, a, b, p, q)

base_points_x = [0.0, 0.5, 1.0]
base_points_y = [0.0, 1.0, 0.0]
trans_points_x = [p, p + 1/(2*b), p + 1/b]
trans_points_y = [q, a + q, q]

# --- Plotlyによるグラフ描画 ---
fig = go.Figure()

# 基本グラフ
fig.add_trace(go.Scatter(
    x=x, y=y_base, mode='lines',
    name="元のテントマップ: y = f(x)",
    line=dict(color='gray', width=2, dash='dash'),
    opacity=0.7
))

# 変換後グラフ
fig.add_trace(go.Scatter(
    x=x, y=y_trans, mode='lines',
    name="変換後: y = a f(b(x-p)) + q",
    line=dict(color='#d62728', width=3)
))

# 元の頂点と両端
fig.add_trace(go.Scatter(
    x=base_points_x, y=base_points_y, mode='markers',
    marker=dict(color='gray', size=6),
    showlegend=False
))

# 変換後の頂点と両端
fig.add_trace(go.Scatter(
    x=trans_points_x, y=trans_points_y, mode='markers',
    marker=dict(color='#d62728', size=10),
    showlegend=False
))

# レイアウト設定
fig.update_layout(
    font=dict(family="Noto Sans CJK JP, Meiryo, 'Yu Gothic', sans-serif"),
    xaxis=dict(
        range=[-11, 12.5], dtick=1,
        zeroline=True, zerolinecolor='black', zerolinewidth=1.5,
        gridcolor='lightgray'
    ),
    yaxis=dict(
        range=[-10, 10], dtick=1,
        zeroline=True, zerolinecolor='black', zerolinewidth=1.5,
        gridcolor='lightgray',
        scaleanchor="x", scaleratio=1  # 縦横比を1:1に固定して歪みを防ぐ
    ),
    plot_bgcolor='white',
    width=800,  
    height=750, 
    margin=dict(l=20, r=20, t=40, b=20),
    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
)

# StreamlitでPlotlyグラフを表示
st.plotly_chart(fig, use_container_width=False)

# --- ダウンロード機能の追加 ---
st.markdown("### 💾 グラフのダウンロード")
col_dl1, col_dl2 = st.columns(2)

with col_dl1:
    # グラフをそのまま動かせるHTMLとしてダウンロード
    html_str = fig.to_html(include_plotlyjs="cdn")
    st.download_button(
        label="🌐 グラフをHTMLで保存",
        data=html_str,
        file_name="tent_map_graph.html",
        mime="text/html"
    )

with col_dl2:
    # PDF形式でダウンロード (kaleido パッケージが必要)
    try:
        pdf_bytes = fig.to_image(format="pdf")
        st.download_button(
            label="📄 グラフをPDFで保存",
            data=pdf_bytes,
            file_name="tent_map_graph.pdf",
            mime="application/pdf"
        )
    except ValueError:
        # kaleidoがインストールされていない場合のエラーメッセージ
        st.warning("⚠️ PDF形式で保存するには、Python環境に `kaleido` パッケージが必要です。ターミナルで `pip install kaleido` を実行してください。")


# --- 解説セクション ---
with st.expander("📝 パラメータによる変化の仕組み"):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(r"""
        **拡大・縮小・反転 ($a, b$)**
        * **$a$**: 縦方向の倍率です。$a=-1$ にすると**上下反転**し、山の形が谷になります。
        * **$b$**: 横方向の倍率です。$b=2$ にすると横幅は**半分** ($1/2$) に圧縮されます。$b$ をマイナスにすると**左右反転**します。
        """)
    with col2:
        st.markdown(r"""
        **平行移動 ($p, q$)**
        * **$p$**: 横（$x$ 軸）方向の平行移動です。
        * **$q$**: 縦（$y$ 軸）方向の平行移動です。
        * 頂点 $(1/2, 1)$ は、変換によって $(p + \frac{1}{2b}, a + q)$ に移動します。
        """)
