import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import os

# --- ⚠️ IMPORTANT: USER CONFIGURATION (FRONT SIDE) ---
FRONT_TEMPLATE_PATH = "updatedfront.png"
FRONT_PHOTO_COORDS = (45, 337)
FRONT_PHOTO_SIZE = (190, 217)
FRONT_VEHICLE_COORDS = (758, 503)
FRONT_VEHICLE_SIZE = (240, 135)
FRONT_NAME_COORDS = (430, 333)
FRONT_FATHER_NAME_COORDS = (701, 333)
FRONT_DESIGNATION_COORDS = (532, 370)
FRONT_SR_NO_COORDS = (89.8, 273)
FRONT_START_COORDS = (430, 445)
FRONT_END_COORDS = (630, 445)
FRONT_DYNAMIC_FONT_NAME = "arialbd.ttf"
try:
    FRONT_DEFAULT_FONT = ImageFont.truetype("ArchivoBlack-Regular.ttf", size=20)
    FRONT_SR_NO_FONT = ImageFont.truetype("ArchivoBlack-Regular.ttf", size=20)
except IOError:
    print("Default fonts not found, using default font for Front.")
    FRONT_DEFAULT_FONT = ImageFont.load_default()
    FRONT_SR_NO_FONT = ImageFont.load_default()
FRONT_TEXT_COLOR = (0, 0, 0)
FRONT_SR_NO_COLOR = (255, 0, 0)
# --- END OF FRONT SIDE CONFIGURATION ---


# --- ⚠️ IMPORTANT: USER CONFIGURATION (BACK SIDE) ---
BACK_TEMPLATE_PATH = "BackTemplate.jpg"
BACK_CNIC_COORDS = (300, 175)
BACK_DOB_COORDS = (300, 211)
BACK_ADDRESS_COORDS = (300, 250)
BACK_HOLDER_NO_COORDS = (816, 627)
BACK_QR_COORDS = (775, 118)
BACK_QR_SIZE = (240, 204)
try:
    BACK_DEFAULT_FONT = ImageFont.truetype("MomoTrustDisplay-Regular.ttf", size=26)
    BACK_ADDRESS_FONT = ImageFont.truetype("MomoTrustDisplay-Regular.ttf", size=21)
    BACK_HOLDER_FONT = ImageFont.truetype("ArchivoBlack-Regular.ttf", size=24)
except IOError:
    print("Default fonts not found, using default font for Back.")
    BACK_DEFAULT_FONT = ImageFont.load_default()
    BACK_HOLDER_FONT = ImageFont.load_default()
    BACK_ADDRESS_FONT = ImageFont.load_default()
BACK_TEXT_COLOR = (0, 0, 0)
BACK_HOLDER_NO_COLOR = (255, 255, 255)
# --- END OF BACK SIDE CONFIGURATION ---


# --- ⚠️ NEW CONFIGURATION: MACHINE IMAGE MAP ---
MACHINE_IMAGE_FOLDER = "machine_images"
MACHINE_MAP = {
    "Trailer Driver": "trailer.png",
    "Forklifter Operator": "forklifter.png",
    "Excavator Operator": "excavator.png",
    "Mobile Crane Operator": "crane.png",
    "Shovel Operator": "shovel.png",
    "Roller Operator": "roller.png",
    "Damper Driver": "dumper.png",
    "Bulldozer Operator": "doser.png",
    "Car Driver": "car.png",
    "JCB Operator": "jcb.png",
    "Grader Operator": "grader.png",
    "Bobcat Operator": "bobcat.png",
    "Hiace Driver": "hiace.png",
    "Rigger": "rigger.png",
    # --- ADD ALL YOUR OTHER COURSES HERE ---
    # "Example Course": "example_machine.png",
}
# --- END OF NEW CONFIGURATION ---


# --- ⚠️ NEW CONFIGURATION: DIPLOMA CROP COORDINATES ---
DIPLOMA_PHOTO_BOX = (1188, 208, 1339, 364)
DIPLOMA_QR_BOX = (1154, 772, 1328, 938)
# --- (Vehicle Box is removed) ---


def remove_white_background(image):
    """Converts white pixels in an image to transparent (Used for the QR code)."""
    img = image.convert("RGBA")
    datas = img.getdata()
    newData = []
    threshold = 240
    for item in datas:
        if item[0] > threshold and item[1] > threshold and item[2] > threshold:
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)
    img.putdata(newData)
    return img

def process_single_card(student_data):
    """
    This is the main "engine". It takes one student's data (a 'row')
    and generates the front and back cards for them.
    """
    try:
        # --- 1. Get all data from the row ---
        # We use str() to make sure pandas data (like numbers) is treated as text
        front_name = str(student_data['StudentName'])
        front_father_name = str(student_data['FatherName'])
        front_designation = str(student_data['Designation'])
        front_start = str(student_data['CourseStart'])
        front_end = str(student_data['CourseEnd'])
        front_sr_no = str(student_data['SrNo'])
        
        try:
            dynamic_font_size = int(student_data['NameFontSize'])
        except ValueError:
            print(f"  [WARN] Invalid font size for {front_sr_no}. Defaulting to 22.")
            dynamic_font_size = 22

        back_cnic = str(student_data['CNIC'])
        back_dob = str(student_data['DOB'])
        back_address = str(student_data['Address']).upper()
        back_holder_no = str(student_data['HolderNo'])
        
        diploma_image_path = str(student_data['DiplomaScanPath'])

        # --- 2. Check that all required files exist ---
        if not os.path.exists(diploma_image_path):
            print(f"  [ERROR] Diploma scan not found for {front_sr_no}: {diploma_image_path}")
            return # Skip this student
        
        machine_filename = MACHINE_MAP.get(front_designation)
        if not machine_filename:
            print(f"  [ERROR] No machine image found for designation: '{front_designation}'")
            return # Skip this student
            
        machine_image_path = os.path.join(MACHINE_IMAGE_FOLDER, machine_filename)
        if not os.path.exists(machine_image_path):
            print(f"  [ERROR] Machine image file not found: {machine_image_path}")
            return # Skip this student

        # --- 3. Load dynamic fonts ---
        try:
            dynamic_font = ImageFont.truetype(FRONT_DYNAMIC_FONT_NAME, size=dynamic_font_size)
        except IOError:
            print(f"  [ERROR] Font file '{FRONT_DYNAMIC_FONT_NAME}' not found.")
            return # Stop processing this card

        # --- 4. Crop images from diploma ---
        source_diploma = Image.open(diploma_image_path).convert("RGBA")
        photo_img = source_diploma.crop(DIPLOMA_PHOTO_BOX)
        qr_img = source_diploma.crop(DIPLOMA_QR_BOX)

        # --- 5. Generate Front Card ---
        card_front = Image.open(FRONT_TEMPLATE_PATH).convert("RGBA")
        
        # Paste Student Photo
        photo_img = photo_img.resize(FRONT_PHOTO_SIZE, Image.LANCZOS)
        card_front.paste(photo_img, FRONT_PHOTO_COORDS, photo_img)
        
        # Paste Vehicle Image
        vehicle_img = Image.open(machine_image_path).convert("RGBA")
        vehicle_img = vehicle_img.resize(FRONT_VEHICLE_SIZE, Image.LANCZOS)
        card_front.paste(vehicle_img, FRONT_VEHICLE_COORDS, vehicle_img)

        # Draw text
        draw_front = ImageDraw.Draw(card_front)
        draw_front.text(FRONT_NAME_COORDS, front_name, font=dynamic_font, fill=FRONT_TEXT_COLOR)
        draw_front.text(FRONT_FATHER_NAME_COORDS, front_father_name, font=dynamic_font, fill=FRONT_TEXT_COLOR)
        draw_front.text(FRONT_DESIGNATION_COORDS, front_designation, font=FRONT_DEFAULT_FONT, fill=FRONT_TEXT_COLOR)
        draw_front.text(FRONT_START_COORDS, front_start, font=FRONT_DEFAULT_FONT, fill=FRONT_TEXT_COLOR)
        draw_front.text(FRONT_END_COORDS, front_end, font=FRONT_DEFAULT_FONT, fill=FRONT_TEXT_COLOR)
        draw_front.text(FRONT_SR_NO_COORDS, front_sr_no, font=FRONT_SR_NO_FONT, fill=FRONT_SR_NO_COLOR)
        
        output_front_filename = f"pvctoday/{front_sr_no}_front.png"
        card_front.save(output_front_filename)

        # --- 6. Generate Back Card ---
        card_back = Image.open(BACK_TEMPLATE_PATH).convert("RGBA")
        draw_back = ImageDraw.Draw(card_back)

        # Draw text
        draw_back.text(BACK_CNIC_COORDS, back_cnic, font=BACK_DEFAULT_FONT, fill=BACK_TEXT_COLOR)
        draw_back.text(BACK_DOB_COORDS, back_dob, font=BACK_DEFAULT_FONT, fill=BACK_TEXT_COLOR)
        draw_back.text(BACK_ADDRESS_COORDS, back_address, font=BACK_ADDRESS_FONT, fill=BACK_TEXT_COLOR)
        draw_back.text(BACK_HOLDER_NO_COORDS, back_holder_no, font=BACK_HOLDER_FONT, fill=BACK_HOLDER_NO_COLOR)

        # Paste the QR code
        qr_img_transparent = remove_white_background(qr_img)
        qr_img_resized = qr_img_transparent.resize(BACK_QR_SIZE, Image.LANCZOS)
        card_back.paste(qr_img_resized, BACK_QR_COORDS, qr_img_resized)

        output_back_filename = f"pvctoday/{front_sr_no}_back.png"
        card_back.save(output_back_filename)

        print(f"  [SUCCESS] Successfully generated cards for {front_sr_no}: {front_name}")

    except Exception as e:
        print(f"  [FATAL ERROR] An unexpected error occurred for SR No {student_data.get('SrNo', 'UNKNOWN')}: {e}")

# --- Main Batch Processing Function ---
def main():
    excel_file = 'students.xlsx'
    
    # Check for required files and folders
    if not os.path.exists(excel_file):
        print(f"Error: Data file not found! Please create '{excel_file}' in the same folder.")
        return
        
    if not os.path.exists(FRONT_TEMPLATE_PATH) or not os.path.exists(BACK_TEMPLATE_PATH):
        print(f"Error: Template files not found! Check '{FRONT_TEMPLATE_PATH}' and '{BACK_TEMPLATE_PATH}'.")
        return

    if not os.path.exists(MACHINE_IMAGE_FOLDER):
        print(f"Error: '{MACHINE_IMAGE_FOLDER}' folder not found!")
        return

    if not os.path.exists('pvctoday'):
        print("Creating 'pvctoday' directory for output...")
        os.makedirs('pvctoday')

    print("--- Starting Batch Card Generation ---")
    
    try:
        # Read the Excel file
        df = pd.read_excel(excel_file, dtype=str)
        df = df.fillna("")


# Clean up empty cells (Pandas sometimes calls them "nan")
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return

    print(f"Found {len(df)} students in the data file.")
    print("---")

    # Loop through each row in the Excel file
    # .iterrows() gives us the index and the row data
    for index, row in df.iterrows():
        print(f"Processing student {index + 1} of {len(df)}...")
        process_single_card(row)
        print("---")

    print("--- Batch Processing Complete! ---")

# --- Run the main function when the script is executed ---
if __name__ == "__main__":
    
    # Check required template files once at the start
    if not os.path.exists(FRONT_TEMPLATE_PATH):
        print(f"CRITICAL ERROR: Front template file not found at '{FRONT_TEMPLATE_PATH}'")
    elif not os.path.exists(BACK_TEMPLATE_PATH):
        print(f"CRITICAL ERROR: Back template file not found at '{BACK_TEMPLATE_PATH}'")
    else:
        main()