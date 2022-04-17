import io
import tempfile
import numpy as np
import pandas as pd
import logging
from typing import Optional, Any
from fastapi import FastAPI, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

logger = logging.getLogger(__name__)

app = FastAPI()

# data files
app.mount("/data", StaticFiles(directory="data"), name="data")


@app.post(
    "/process_excel_file/",
    responses={
        200: {
            "content": {"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": {}}
        }
    },
    response_class=FileResponse,
)
def process_excel_file(file: bytes = File(...)) -> Any:
    """
    Process an Excel file.<br>
        Example of Excel file: <a href="data/example_template.xlsx">example_template.xlsx</a><br>
        return: Excel File
    """
    logger.info(f"process_excel_file request: len {len(file)}")

    try:
        df = pd.read_excel(io.BytesIO(file).read())
        rows_count = df.shape[0]
        logger.info(f"process_excel_file df: {df}")
        logger.info(f'dataframe columns {df.columns}')

        # do something with df
        df = pd.DataFrame()
        df['feature_1'] = np.random.randint(1, 1000, rows_count)
        df['feature_2'] = np.random.choice(['a', 'b', 'c'], rows_count)
        df['feature_3'] = np.random.randint(1, 100, rows_count)
        df['feature_4'] = np.random.choice([True, False], rows_count)
        df['predicted_rate'] = np.random.randint(1, 100, rows_count)

        stream = io.BytesIO()
        df.to_excel(stream, index=False)
        stream.seek(0)
        with tempfile.NamedTemporaryFile(mode="w+b", suffix=".xlsx", delete=False) as FOUT:
            FOUT.write(stream.read())
            return FileResponse(
                FOUT.name,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={
                    "Content-Disposition": "attachment; filename=predictions.xlsx",
                    "Access-Control-Expose-Headers": "Content-Disposition",
                }
            )
    except HTTPException as hex:
        logger.error(hex)
        raise hex
    except Exception as ex:
        logger.error(ex)
        raise HTTPException(status_code=400, detail=str(ex))
