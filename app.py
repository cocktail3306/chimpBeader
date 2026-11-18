import streamlit as st
from PIL import Image, ImageSequence
import numpy as np
import tempfile
import os

st.set_page_config(page_title="Beard Overlay", page_icon="🧔")
st.title("🧔 Beard Overlay")
st.write("Charge le GIF sur lequel tu veux coller la barbe.")

# Le GIF de barbe doit être dans le même dossier que app.py
BEARD_PATH = "beard.gif"

uploaded_file = st.file_uploader("Ton GIF", type=["gif"])

col1, col2 = st.columns(2)
with col1:
    dx = st.slider("Décalage X", -150, 150, 0)
with col2:
    dy = st.slider("Décalage Y", -150, 150, 0)

if st.button("Ajouter la barbe", type="primary") and uploaded_file is not None:
    if not os.path.exists(BEARD_PATH):
        st.error("Fichier beard.gif manquant")
    else:
        beard = Image.open(BEARD_PATH)
        target = Image.open(uploaded_file)

        beard_frames = [np.array(f.convert("RGB")) for f in ImageSequence.Iterator(beard)]
        target_frames = [np.array(f.convert("RGB")) for f in ImageSequence.Iterator(target)]

        if len(beard_frames) != len(target_frames):
            st.error(f"Le GIF doit avoir {len(beard_frames)} frames")
        else:
            result_frames = []
            for b_arr, t_arr in zip(beard_frames, target_frames):
                t_arr = t_arr.copy()
                mask = ~np.all(b_arr == [255, 255, 255], axis=2)
                ys, xs = np.where(mask)

                for y, x in zip(ys, xs):
                    ty = int(y + dy)
                    tx = int(x + dx)
                    if 0 <= ty < t_arr.shape[0] and 0 <= tx < t_arr.shape[1]:
                        t_arr[ty, tx] = b_arr[y, x]

                result_frames.append(Image.fromarray(t_arr))

            out_path = tempfile.mktemp(suffix=".gif")
            result_frames[0].save(
                out_path,
                save_all=True,
                append_images=result_frames[1:],
                duration=beard.info.get("duration", 100),
                loop=0,
                optimize=True
            )

            st.image(out_path)
            with open(out_path, "rb") as f:
                st.download_button("Télécharger le GIF", f, file_name="bearded.gif")