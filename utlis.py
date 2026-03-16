import string
import easyocr  

#initialize easyocr
reader=easyocr.Reader(['en'],gpu=False)

#mapping dictionaries 
dict_char_to_int={'O':'0',
                  'I':'1',
                  'J':'3',
                  'A':'4',
                  'G':'6',
                  'S':'5'}

dict_int_to_char={'0':'O',
                  '1':'I',
                  '3':'J',
                  '4':'A',
                  '6':'G',
                  '5':'S'}

def write_csv(results,output_path) :
  """
  Write results to csv file 
  results: Dictionary containing results 
  output_path: path to the output csv file 
  """

  with open(output_path,'w') as f:
    f.write('{},{},{},{},{},{},{}\n'.format('frame_nmr','car_id','car_bbox','license_plate_bbox','license_plate_bbox_score','license_number','license_number_score'))

    for frame_nmr in results.keys():
      for car_id in results[frame_nmr].keys():
        print(results[frame_nmr][car_id])
        if 'car' in results[frame_nmr][car_id].keys() and \
        'license_plate' in results[frame_nmr][car_id].keys() and \
        'text' in results[frame_nmr][car_id]['license_plate'].keys():
          f.write('{},{},{},{},{},{},{}\n'.format(frame_nmr,
                                               car_id,
                                               '[{} {} {} {}]'.format(
                                                 results[frame_nmr][car_id]['car']['bbox'][0],
                                                 results[frame_nmr][car_id]['car']['bbox'][1],
                                                 results[frame_nmr][car_id]['car']['bbox'][2],
                                                 results[frame_nmr][car_id]['car']['bbox'][3]),
                                               '[{} {} {} {}]'.format(
                                                 results[frame_nmr][car_id]['license_plate']['bbox'][0],
                                                 results[frame_nmr][car_id]['license_plate']['bbox'][1],
                                                 results[frame_nmr][car_id]['license_plate']['bbox'][2],
                                                 results[frame_nmr][car_id]['license_plate']['bbox'][3]),
                                               results[frame_nmr][car_id]['license_plate']['bbox_score'],
                                               results[frame_nmr][car_id]['license_plate']['text'],
                                               results[frame_nmr][car_id]['license_plate']['text_score'])
                                               )

def license_compiles_format(text):
  #check if text extracted using ocr matches the standard format on which we are working on
  # ltr:letter num:number
  # ltr1_ltr2_num1_num2_rndmltr1_rndmltr2_rndmltr3
  # SM12ABC

  if len(text)!=7:
    return False
  
  if(text[0] in string.ascii_uppercase or text[0] in dict_int_to_char.keys()) and \
    (text[1] in string.ascii_uppercase or text[1] in dict_int_to_char.keys()) and \
    (text[2] in ['1','2','3','4','5','6','7','8','9','0'] or text[2] in dict_char_to_int.keys()) and\
    (text[3] in ['1','2','3','4','5','6','7','8','9','0'] or text[3] in dict_char_to_int.keys()) and\
    (text[4] in string.ascii_uppercase or text[4] in dict_int_to_char.keys()) and \
    (text[5] in string.ascii_uppercase or text[5] in dict_int_to_char.keys()) and \
    (text[6] in string.ascii_uppercase or text[6] in dict_int_to_char.keys()):
    return True
  else:
    return False

def format_license(text):
  #takes normal license plate text extracted using easyocr and return formatted license plate 
  #we use mapping dictionaries for doing so 
  #we take index's of text from 0 -> 6 
  #we know we have text at index 0,1,4,5,6
  #number at index 2,3

  license_plate_=''
  mapping={0:dict_int_to_char,1:dict_int_to_char,4:dict_int_to_char,5:dict_int_to_char,6:dict_int_to_char,
           2:dict_char_to_int,3:dict_char_to_int}
  
  for j in [0,1,2,3,4,5,6]:
    if text[j]in mapping[j].keys():
      license_plate_+=mapping[j][text[j]]
    else:
      license_plate_+=text[j]

  return license_plate_
  
def read_license_plate(license_plate_crop):
  #we created reader instance using easyocr which reads the text from image 
  #we store teh output in detctions list 
  #it will have fields like bbox cords,text,confidence score of read text 
  #we check the format of text we got with std format 
  #and if it matches then return the text and its confidence score
  detections=reader.readtext(license_plate_crop)

  for detection in detections:
    bbox,text,score=detection

    text=text.upper().replace(' ','')

    if license_compiles_format(text):
      return format_license(text),score
  
  return None,None

def get_car(license_plate,vehicle_track_ids):
# it takes license_plate as object which has x1,y1,x2,y2,class_id and 
# track_id which has x1,x2,x2,y2 and unique id assigned to unique vehicle 
# then function returns tuple vehicle cordinates and car_id which has that license_plate
  x1,y1,x2,y2,score,class_id=license_plate

  foundIt=False
  for j in range(len(vehicle_track_ids)):
    car_x1, car_y1, car_x2, car_y2,car_id=vehicle_track_ids[j]

    if x1 > car_x1 and y1 >car_y1 and x2 <car_x2 and y2 < car_y2:
      car_index=j
      foundIt=True
      break
  if foundIt:
    return vehicle_track_ids[car_index] 

  return -1,-1,-1,-1,-1

