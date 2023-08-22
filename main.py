import streamlit as st
import base64
import os
from optimize_images.api import optimize_as_batch
from optimize_images.data_structures import OutputConfiguration
import uuid
import shutil

def make_archive(source, destination):
    base_name = '.'.join(destination.split('.')[:-1])
    format = destination.split('.')[-1]
    root_dir = os.path.dirname(source)
    base_dir = os.path.basename(source.strip(os.sep))

    # Xóa tất cả các file zip trước đó
    for item in os.listdir(root_dir):
        if item.endswith('.zip'):
            os.remove(os.path.join(root_dir, item))

    shutil.make_archive(base_name, format, root_dir, base_dir)
    shutil.rmtree(source)


def resize_image(image, max_width, max_height):
    if max_width == 0:
        max_width = image.width
    if max_height == 0:
        max_height = image.height

    resized_image = image.resize((max_width, max_height))
    return resized_image


def save_uploaded_image(uploaded_file, folder_path):
    filename = uploaded_file.name
    image_path = os.path.join(folder_path, filename)
    with open(image_path, "wb") as f:
        f.write(uploaded_file.getvalue())
    return image_path



def optimize_images(
    src_path,
    quality,
    max_w,
    max_h,
    watch_dir: bool = False,
    recursive: bool = True,
    remove_transparency: bool = False,
    reduce_colors: bool = False,
    max_colors: int = 256,
    keep_exif: bool = False,
    convert_all: bool = True,
    conv_big: bool = False,
    force_del: bool = True,
    grayscale: bool = False,
    ignore_size_comparison: bool = False,
    fast_mode: bool = True,
    jobs: int = 0,
):
    output_config = OutputConfiguration(show_only_summary=False, show_overall_progress=False, quiet_mode=False)
    bg_color = (255, 255, 255)
    print(src_path, quality)

    message_img_status, message_report = optimize_as_batch(
        src_path,
        watch_dir,
        recursive,
        quality,
        remove_transparency,
        reduce_colors,
        max_colors,
        max_w,
        max_h,
        keep_exif,
        convert_all,
        conv_big,
        force_del,
        bg_color,
        grayscale,
        ignore_size_comparison,
        fast_mode,
        jobs,
        output_config
    )

    print(message_report)

    # Trả về chuỗi JSON trong phản hồi của API
    return message_report


def create_download_zip(zip_directory, zip_path, filename='optimized_images.zip'):
    """
    zip_directory (str): path to directory you want to zip
    zip_path (str): where you want to save zip file
    filename (str): download filename for the user who downloads this
    """
    shutil.make_archive(zip_path, 'zip', zip_directory)
    with open(zip_path, 'rb') as f:
        bytes = f.read()
        b64 = base64.b64encode(bytes).decode()
        href = f'<a href="data:application/zip;base64,{b64}" download="{filename}">\
            Download Optimized Images\
        </a>'
        st.markdown(href, unsafe_allow_html=True)


def get_binary_file_download_link(file_data, file_name, link_text):
    b64 = base64.b64encode(file_data).decode()
    return f'<a href="data:application/zip;base64,{b64}" download="{file_name}">{link_text}</a>'


def main():
    st.title("Image Optimization Eco")
    st.write("Upload images, set parameters, optimize their size, and download the results!")

    uploaded_files = st.file_uploader("Upload images", type=["jpg", "png", "jpeg"], accept_multiple_files=True)

    if uploaded_files is not None and len(uploaded_files) > 0:
        quality = st.slider("Quality", min_value=1, max_value=100, value=35, help="Điều chỉnh chất lượng nén hình ảnh. Giá trị cao hơn mang lại chất lượng hình ảnh tốt hơn nhưng kích thước tệp lớn hơn.")
        max_width = st.number_input("Max Width", min_value=0, value=0, help="Nhập 0 để giữ nguyên chiều rộng ban đầu. Nhập giá trị pixel để thay đổi kích thước chiều rộng của hình ảnh.")
        max_height = st.number_input("Max Height", min_value=0, value=0, help="Nhập 0 để giữ nguyên chiều cao ban đầu. Nhập giá trị pixel để thay đổi kích thước chiều cao hình ảnh.")

        if st.button("Optimize"):
            with st.spinner("Optimizing..."):
                folder_name = str(uuid.uuid4())
                image_folder = os.path.join("images", folder_name)
                os.makedirs(image_folder, exist_ok=True)

            st.subheader("Optimized Images")
            for i, optimized_image in enumerate(uploaded_files):
                st.image(optimized_image, caption=f"Optimized Image {i + 1}", width=300)
                save_uploaded_image(optimized_image, image_folder)

            message_report = optimize_images(src_path=image_folder, quality=quality, max_w=max_width, max_h=max_height)
            st.write("Optimization Report:")
            st.write(message_report)
            make_archive(image_folder, f'{image_folder}.zip')


            with open(f'{image_folder}.zip', 'rb') as f:
                st.download_button('Download Zip', f, file_name='archive.zip')


if __name__ == "__main__":
    main()
