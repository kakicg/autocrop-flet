import cv2
import numpy as np
import os

def process_image(camera_path, filename, processed_folder="./processed_images"):
    # 画像を読み込む
    image = cv2.imread(camera_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 30, 255, cv2.THRESH_BINARY)
    # カーネルの定義
    kernel = np.ones((5, 5), np.uint8)
    # オープニング処理（ノイズ除去）
    opening = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
    # 物体を結合するためのダイレーション処理
    dilated = cv2.dilate(opening, kernel, iterations=2)
    # ダイレーション後の輪郭を検出
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # 輪郭に基づいてバウンディングボックスを描画
    bounding_boxes = []
    for contour in contours:
        # 輪郭に外接する長方形（バウンディングボックス）を計算
        x, y, w, h = cv2.boundingRect(contour)
        bounding_boxes.append([x, y, x + w, y + h])

    # バウンディングボックス同士を結合する関数
    def merge_boxes(boxes):
        if len(boxes) == 0:
            return []

        # バウンディングボックスの最小と最大の座標を初期化
        x_min = min([box[0] for box in boxes])
        y_min = min([box[1] for box in boxes])
        x_max = max([box[2] for box in boxes])
        y_max = max([box[3] for box in boxes])

        return [[x_min, y_min, x_max, y_max]]

    # すべてのバウンディングボックスを結合
    merged_boxes = merge_boxes(bounding_boxes)
    # 結合されたバウンディングボックスを描画（赤色の矩形）
    for box in merged_boxes:
        cv2.rectangle(image, (box[0], box[1]), (box[2], box[3]), (0, 0, 255), 2)
    
    estimated_height = image.shape[0]
    if len(merged_boxes)>0:
        estimated_height = estimated_height - merged_boxes[0][1]
    print(f"estimated_height:{estimated_height}")
    outerbox_height = estimated_height
    top_margin = 80
    if image.shape[0] - estimated_height >= top_margin:
        outerbox_height += top_margin
    else:
        outerbox_height = image.shape[0]
    outerbox_width = outerbox_height * 9 // 16
    left = (image.shape[1] - outerbox_width)//2
    top = image.shape[0] - outerbox_height
    top_left = (left, top)
    print(f"top_left:{top_left}")

    bottom_right = (left + outerbox_width , image.shape[0])
    print(f"bottom_right:{bottom_right}")

    cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)

    # 結果をファイルとして保存する
    os.makedirs(processed_folder, exist_ok=True)  # 保存先フォルダを作成
    output_file_path = os.path.join(processed_folder, filename)
    cv2.imwrite(output_file_path, image)
    print(f"画像が '{output_file_path}' として保存されました。")
    return estimated_height, output_file_path

