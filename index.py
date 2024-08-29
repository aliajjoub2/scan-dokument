import cv2
import numpy as np
from PIL import Image
from fpdf import FPDF

# قائمة لتخزين النقاط المحددة
points = []

# الدالة لتحويل المنظور وحفظ الصورة وإنشاء ملف PDF
def transform_and_save():
    global points, frame
    if len(points) == 4:
        # ترتيب النقاط للحصول على مصفوفة التحويل
        points_array = np.array(points, dtype="float32")
        (tl, tr, br, bl) = points_array

        # حساب العرض والارتفاع الجديدين للصورة
        widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        maxWidth = max(int(widthA), int(widthB))

        heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        maxHeight = max(int(heightA), int(heightB))

        # النقاط المستهدفة لتحويل المنظور
        dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]], dtype="float32")

        # حساب مصفوفة التحويل وتطبيقها
        matrix = cv2.getPerspectiveTransform(points_array, dst)
        warped = cv2.warpPerspective(frame, matrix, (maxWidth, maxHeight))

        # حفظ الصورة المعدلة
        image_name = "scanned_image.jpg"
        cv2.imwrite(image_name, warped)
        
        # إنشاء ملف PDF وحفظ الصورة فيه
        pdf = FPDF()
        pdf.add_page()
        pdf.image(image_name, x=0, y=0, w=210, h=297)  # ضبط الصورة لتتناسب مع صفحة A4
        pdf.output("output.pdf")

        print("تم إنشاء ملف PDF باسم output.pdf")

        # إغلاق جميع النوافذ بعد حفظ ملف الـ PDF
        cv2.destroyAllWindows()
    else:
        print("لم يتم تحديد الحواف بشكل صحيح.")

# وظيفة لاستدعاء الأحداث من النقر بالماوس
def mouse_click(event, x, y, flags, param):
    global points, img
    if event == cv2.EVENT_LBUTTONDOWN:
        points.append((x, y))
        cv2.circle(img, (x, y), 5, (0, 255, 0), -1)
        cv2.imshow("تحديد الحواف", img)
        
        # التحقق من تحديد 4 نقاط
        if len(points) == 4:
            # تطبيق تحويل المنظور مباشرة بعد تحديد النقاط الأربعة
            transform_and_save()

# فتح الكاميرا
cap = cv2.VideoCapture(0)

print("اضغط على 'c' لالتقاط الصورة")

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    cv2.imshow("كاميرا", frame)
    
    key = cv2.waitKey(1)
    if key == ord('c'):
        img = frame.copy()
        cv2.imshow("تحديد الحواف", img)
        cv2.setMouseCallback("تحديد الحواف", mouse_click)
        break

cap.release()
cv2.waitKey(0)
cv2.destroyAllWindows()
