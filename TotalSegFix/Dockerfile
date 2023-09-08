from python:3.7

RUN pip install --no-cache-dir SimpleITK==2.0.2 p_tqdm numpy

COPY fix_sitk_orthoginal.py /app/

ENTRYPOINT ["python", "/app/fix_sitk_orthoginal.py"]
