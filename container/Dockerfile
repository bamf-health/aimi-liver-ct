FROM pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime

# specify cuda and nnunet specific environment variables
ENV NVIDIA_VISIBLE_DEVICES all
ENV NVIDIA_DRIVER_CAPABILITIES compute,utility

# FIXME: set this environment variable as a shortcut to avoid nnunet crashing the build
# by pulling sklearn instead of scikit-learn
# N.B. this is a known issue:
# https://github.com/MIC-DKFZ/nnUNet/issues/1281
# https://github.com/MIC-DKFZ/nnUNet/pull/1209
ENV SKLEARN_ALLOW_DEPRECATED_SKLEARN_PACKAGE_INSTALL=True

# Install system utilities and CUDA related dependencies
ENV DEBIAN_FRONTEND noninteractive
RUN apt update && apt install -y --no-install-recommends \
    dcm2niix \
    wget \
    vim \
    p7zip \
    p7zip-full \
    zip \
    unzip \
    ffmpeg \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Set work dirs
RUN mkdir /app /app/data /app/data/input_data /app/data/output_data
WORKDIR /app
ENV PATH="/root/.local/bin:${PATH}"

# setup nnunet environment variables
ENV nnUNet_raw_data_base="/nnunet_data/nnUNet_raw_data_base/"
ENV nnUNet_preprocessed="/nnunet_data/nnUNet_preprocessed/"
ENV RESULTS_FOLDER="/nnunet_data/nnUNet_trained_models/"
ENV WEIGHTS_DIR="$RESULTS_FOLDER/nnUNet/"
RUN mkdir -p $nnUNet_raw_data_base
RUN mkdir -p $nnUNet_preprocessed
RUN mkdir -p $WEIGHTS_DIR

# Pull nnUNet model weights into the container for Task773_Liver
ENV TASK_NAME=Task773_Liver
ENV WEIGHTS_FN=$TASK_NAME.zip
ENV WEIGHTS_URL=https://zenodo.org/record/8274976/files/$WEIGHTS_FN
RUN wget --directory-prefix ${WEIGHTS_DIR} ${WEIGHTS_URL} --no-check-certificate
RUN unzip ${WEIGHTS_DIR}${WEIGHTS_FN} -d ${WEIGHTS_DIR}
RUN rm ${WEIGHTS_DIR}${WEIGHTS_FN}

# Install binaries for itkimage2segimage package
ENV PACKAGE_DIR="/root/.local/bin/"
ENV PACKAGE_TAR="dcmqi-1.2.5-linux.tar.gz"
ENV DCMQI_PACKAGE_PATH="${PACKAGE_DIR}dcmqi-1.2.5-linux"
ENV ITKIMAGE2SEGIMAGE_URL=https://github.com/QIICR/dcmqi/releases/download/v1.2.5/${PACKAGE_TAR}
RUN wget --directory-prefix ${PACKAGE_DIR} ${ITKIMAGE2SEGIMAGE_URL} --no-check-certificate
RUN tar -zxvf ${PACKAGE_DIR}${PACKAGE_TAR}
RUN rm ${PACKAGE_DIR}${PACKAGE_TAR}

# Install python tools needed for nnUNet inference
RUN pip install --user --upgrade pip
RUN pip install --user --no-cache-dir \
    nnunet \
    pydicom \
    SimpleITK \
    dcm2niix \
    pyyaml \
    scikit-build \
    pynrrd

ENV MKL_THREADING_LAYER=GNU

# Copy scripts and config
COPY app/src/* /app/
COPY app/dcm-meta/ai-dicom-seg-meta.json /app/

# Execute the script
ENTRYPOINT ["python3", "run.py", "/data/input", "/data/output"]