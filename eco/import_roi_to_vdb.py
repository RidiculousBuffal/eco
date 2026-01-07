import asyncio
import logging
import time
from tqdm.asyncio import tqdm
from eco.agents.ROIdistillation import ROIdistillation
from eco.data.preprocess import Data

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


async def process_single_item(roi_agent, data_item, semaphore):
    async with semaphore:
        start_time = time.time()
        try:
            # 1. 调用大模型提取 ROI
            roi = await roi_agent.call(data_item.src_code, data_item.tgt_code)
            duration = time.time() - start_time
            return roi, data_item
        except Exception as e:
            logger.error(f"Failed to process {data_item.src_id}: {str(e)}")
            return None, None


async def process():
    # 1. 加载数据
    logger.info("Loading processed data...")
    datas = Data().getProcessedData()
    # datas = datas[3000:5000]
    total_count = len(datas)
    logger.info(f"Total items to process: {total_count}")

    roi_agent = ROIdistillation()
    MAX_CONCURRENT = 20  # 最大并发请求数
    BATCH_SIZE = 20  # 批量入库大小
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)

    tasks = [process_single_item(roi_agent, d, semaphore) for d in datas]

    pending_rois = []
    pending_metadatas = []

    success_count = 0
    fail_count = 0
    total_embedded = 0

    start_process_time = time.time()

    logger.info(f"Starting ROI Distillation with concurrency={MAX_CONCURRENT}...")

    for response in tqdm(asyncio.as_completed(tasks), total=total_count, desc="Processing ROIs"):
        roi, metadata = await response

        if roi:
            success_count += 1
            pending_rois.append(roi)
            pending_metadatas.append(metadata)
        else:
            fail_count += 1

        if len(pending_rois) >= BATCH_SIZE:
            batch_start = time.time()
            try:
                await roi_agent.batchEmbeddingROI(pending_rois, pending_metadatas)
                total_embedded += len(pending_rois)
                logger.info(f"Batch Insert: {len(pending_rois)} items (Success: {success_count}, Fail: {fail_count})")
            except Exception as e:
                logger.error(f"Critical error during batch embedding: {e}")
            finally:
                pending_rois = []
                pending_metadatas = []

    if pending_rois:
        try:
            await roi_agent.batchEmbeddingROI(pending_rois, pending_metadatas)
            total_embedded += len(pending_rois)
            logger.info(f"Final Batch Insert: {len(pending_rois)} items.")
        except Exception as e:
            logger.error(f"Critical error during final batch embedding: {e}")

    end_time = time.time()
    total_duration = end_time - start_process_time

    logger.info("=" * 30)
    logger.info("PROCESS COMPLETED")
    logger.info(f"Total Time: {total_duration / 60:.2f} minutes")
    logger.info(f"Total Input: {total_count}")
    logger.info(f"Successful LLM Calls: {success_count}")
    logger.info(f"Failed LLM Calls: {fail_count}")
    logger.info(f"Total Embedded to VDB: {total_embedded}")
    logger.info(f"Avg Speed: {total_duration / total_count:.2f}s per item (with concurrency {MAX_CONCURRENT})")
    logger.info("=" * 30)


if __name__ == '__main__':
    try:
        asyncio.run(process())
    except KeyboardInterrupt:
        logger.warning("Process interrupted by user.")
