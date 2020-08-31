#!/usr/bin/env python
#coding=UTF-8
#IMGCRYPT
#FIUBA - 75.26 Simulacion - 2C2019
#79979 - Gonzalez, Juan Manuel (juanmg0511@gmail.com)
#
#A pseudo-random numbers generator based on a novel 3D chaotic map with an application to color image encryption
#A color image encryption scheme
#https://doi.org/10.1007/s11071-018-4390-z

#Modules and libraries import
import sys, os, getopt, math, pickle
from tqdm import tqdm
from PIL import Image

#General definitions and global variables for program modes
version = "imgcrypt v1.00 - 15/04/2020"
bar_format = "{percentage:3.0f}%|{bar:40}{r_bar}"
lossy_formats = ["jpeg","jpeg2000"]
silent = False
unhurried = False

#Helper functions implementation
#Picewise map
def pMap(x):
    "piecewise map: function that given x and a real control parameter c1, calculates Ψ(x)"
    c1 = 20
    return (abs(1 - (c1 * x)))

#Logistic map
def lMap(x, y):
    "2D logistic map: function that given x, y and a real control parameter c2, calculates Λ(x, y)"
    c2 = 20
    return (c2 * x * (1 - y))

#3D piecewise-logistic map (3D-PLM), T(x, y, z)
def tMap(x, y, z):
    "3D piecewise-logistic map: function that given x, y, z calculates T(x, y, z)"    
    x = (pMap(x) + lMap(y, z)) % 1
    y = (pMap(y) + lMap(z, x)) % 1
    z = (pMap(z) + lMap(x, y)) % 1
    
    return x, y, z

#Discretization function Φ
def phi(amin, amax, d, u):
    "Discretization function Φ:"
    "Φd : [amin, amax] -> [0, ... , d] ; for amin=0 y amax=1"
    "Given amin, amax and d, calculates: u -> Φd(u)"
    
    h = ((abs(amax-amin))/(d+1))
    
    r = 0
    if (u >= amin and u < amax):   
        r = math.floor((u-amin)/h)    
    else:
        r = d

    return (r)

#Function that generates the chaotic masks used by the encryption algorithm
#Original version
def generateChaoticMasks(K, m, n):
    "Generates the chaotic masks using the 3D-PLM"
    "Input:"
    "K: the encryption key"
    "m,n: image size in pixels, height and width respectively"
    "nt: transition parameter for the 3D-PLM"
    "Output:"
    "Chaotic masks Mr, Mg, Mb"
    nt = 10**5

    Cx = []
    Cy = []
    Cz = []

    if (silent==False): pbar = tqdm(total=m*n, bar_format=bar_format, unit="px")
    for i in range(m*n):
        x = K[0]
        y = K[1]
        z = K[2]
        for j in range(nt+i):
            x, y, z = tMap(x, y, z)
        Cx.append(x)
        Cy.append(y)
        Cz.append(z)
        if (silent==False): pbar.update(1)
    if (silent==False): pbar.close()

    Mr = []
    Mg = []
    Mb = []

    for i in range(m*n):
        Mr.append(phi(0,1,(m*n),Cx[i]))
        Mg.append(phi(0,1,(m*n),Cy[i]))
        Mb.append(phi(0,1,(m*n),Cz[i]))

    return Mr, Mg, Mb

#Function that generates the chaotic masks used by the encryption algorithm
#Optimized version
def generateChaoticMasksOptimized(K, m, n):
    "Generates the chaotic masks using the 3D-PLM"
    "Input:"
    "K: the encryption key"
    "m,n: image size in pixels, height and width respectively"
    "nt: transition parameter for the 3D-PLM"
    "Output:"
    "Chaotic masks Mr, Mg, Mb"
    nt = 10**5
    
    Cx = []
    Cy = []
    Cz = []

    x = K[0]
    y = K[1]
    z = K[2]
    for i in range(nt):
        x, y, z = tMap(x, y, z)
    
    if (silent==False): pbar = tqdm(total=m*n, bar_format=bar_format, unit="px")
    for i in range(m*n):
        if (i==0):
            Cx.append(x)
            Cy.append(y)
            Cz.append(z)
        else:
            x, y, z = tMap(Cx[i-1], Cy[i-1], Cz[i-1])
            Cx.append(x)
            Cy.append(y)
            Cz.append(z)
        if (silent==False): pbar.update(1)
    if (silent==False): pbar.close()

    Mr = []
    Mg = []
    Mb = []

    for i in range(m*n):
        Mr.append(phi(0,1,(m*n),Cx[i]))
        Mg.append(phi(0,1,(m*n),Cy[i]))
        Mb.append(phi(0,1,(m*n),Cz[i]))

    return Mr, Mg, Mb

#Function that performs the encryption process
def encryptImage(Kd, Io, m, n):
    "Excecutes the steps required to perform the encryption scheme"
    "Input:"
    "Kd: the initial guess used for x, y and z"
    "Io: the RGB values of each pixel in the original image"
    "m,n: image size in pixels, height and width respectively"
    "Output:"
    "K: the encryption key"
    "Id: the RGB values of each pixel in the encrypted image"   
    
    if (silent==False): print("\nEncrypting image, please wait...")
    d = 8
    
    #Encryption
    #Step 1
    #Preliminary steps
    if (silent==False): print("Step 1/5, preliminary steps:", end=" ")
    Ir = [] 
    Ig = []
    Ib = []

    Ir = [r[0] for r in Io]
    Ig = [g[1] for g in Io]
    Ib = [b[2] for b in Io]
    if (silent==False): print("done!")
    
    #Step 2
    #Generation of the initial conditions
    if (silent==False): print("Step 2/5, generation of the initial conditions:", end=" ")
    Er = sum(Ir)
    Eg = sum(Ig)
    Eb = sum(Ib)

    x0 = Kd[0] + (10**(-(d+8)) * Er)
    y0 = Kd[1] + (10**(-(d+8)) * Eg)
    z0 = Kd[2] + (10**(-(d+8)) * Eb)

    K = (x0, y0, z0)
    if (silent==False): print("done!")

    #Step 3
    #Obtain the shuffled image
    if (silent==False): print("Step 3/5, obtain the shuffled image:")
    x = K[0]
    y = K[1]
    z = K[2]

    kr = 0
    kg = 0
    kb = 0

    Sr = []
    Sg = []
    Sb = []

    if (silent==False): pbar = tqdm(total=m*n,bar_format=bar_format, unit="px")
    for i in range(n*m):
        Sr.append(-1)
        Sg.append(-1)
        Sb.append(-1)

    i = 0
    i_prev = 0
    while (kr < n*m or kg < n*m or kb < n*m):

        x, y, z = tMap(x, y, z)

        if ((Sr[phi(0,1,(m*n)-1,x)]) < 0):
            Sr[phi(0,1,(m*n)-1,x)] = Ir[kr]
            kr = kr + 1
        
        if ((Sg[phi(0,1,(m*n)-1,y)]) < 0):
            Sg[phi(0,1,(m*n)-1,y)] = Ig[kg]
            kg = kg + 1

        if ((Sb[phi(0,1,(m*n)-1,z)]) < 0):
            Sb[phi(0,1,(m*n)-1,z)] = Ib[kb]
            kb = kb + 1
        
        i = kr
        if (kg < i): i = kg
        if (kb < i): i = kb
        if (silent==False):
            if ((i < m*n) and (i != i_prev)): pbar.update(1)
        i_prev = i
    
    if (silent==False):
        if (i <= (m*n)): pbar.update(1)
    if (silent==False): pbar.close()
            
    #Step 4
    #Generate the chaotic masks
    if (silent==False): print("Step 4/5, generate the chaotic masks:")
    if (unhurried == True):
        Mr, Mg, Mb = generateChaoticMasks(K,m,n)
    else:
        Mr, Mg, Mb = generateChaoticMasksOptimized(K,m,n)

    #Step 5
    #Produce the cipher image
    if (silent==False): print("Step 5/5, produce the cipher image:", end=" ")
    Cpr = []
    Cpg = []
    Cpb = []

    for i in range(m*n):
        Cpr.append((Sr[i] + Mr[i]) % 256)
        Cpg.append((Sg[i] + Mg[i]) % 256)
        Cpb.append((Sb[i] + Mb[i]) % 256)

    Ic = []
    for i in range(m*n):
        Ic.append((Cpr[i], Cpg[i], Cpb[i]))
    if (silent==False): print("done!")

    return K, Ic

#Function that performs the decryption process
def decryptImage(K, Ie, m, n):
    "Excecutes the steps required to perform the decryption scheme"
    "Input:"
    "K: the encryption key"
    "Ie: the RGB values of each pixel in the encrypted image"
    "m,n: image size in pixels, height and width respectively"
    "Output:"
    "Id: the RGB values of each pixel in the decrypted image"   
    
    if (silent==False): print("\nDecrypting image, please wait...")
    #Decryption
    #Step 1
    #Preliminary stage
    if (silent==False): print("Step 1/4, preliminary stage:", end=" ")
    Cpr = []
    Cpg = []
    Cpb = []

    Cpr = [r[0] for r in Ie]
    Cpg = [g[1] for g in Ie]
    Cpb = [b[2] for b in Ie]
    if (silent==False): print("done!")
        
    #Step 2
    #Generate the chaotic masks
    if (silent==False): print("Step 2/4, generate the chaotic masks:")
    if (unhurried == True):
        Mr, Mg, Mb = generateChaoticMasks(K,m,n)
    else:
        Mr, Mg, Mb = generateChaoticMasksOptimized(K,m,n)
    
    #Step 3
    #Obtain the shuffled image
    if (silent==False): print("Step 3/4, obtain the shuffled image:", end=" ")
    Sr = []
    Sg = []
    Sb = []

    for i in range(m*n):
        Sr.append((Cpr[i] - Mr[i]) % 256)
        Sg.append((Cpg[i] - Mg[i]) % 256)
        Sb.append((Cpb[i] - Mb[i]) % 256)
    if (silent==False): print("done!")

    #Step 4
    #Retrieve the original image
    if (silent==False): print("Step 4/4, retrieve the original image:")
    x = K[0]
    y = K[1]
    z = K[2]

    kr = 0
    kg = 0
    kb = 0

    Ir = []
    Ig = []
    Ib = []

    if (silent==False): pbar = tqdm(total=m*n,bar_format=bar_format, unit="px")
    i = 0
    i_prev = 0
    while (kr < n*m or kg < n*m or kb < n*m):

        x, y, z = tMap(x, y, z)

        if ((Sr[phi(0,1,(m*n)-1,x)]) >= 0):
            Ir.append(Sr[phi(0,1,(m*n)-1,x)])
            Sr[phi(0,1,(m*n)-1,x)] = -1
            kr = kr + 1

        if ((Sg[phi(0,1,(m*n)-1,y)]) >= 0):
            Ig.append(Sg[phi(0,1,(m*n)-1,y)])
            Sg[phi(0,1,(m*n)-1,y)] = -1
            kg = kg + 1

        if ((Sb[phi(0,1,(m*n)-1,z)]) >= 0):
            Ib.append(Sb[phi(0,1,(m*n)-1,z)])
            Sb[phi(0,1,(m*n)-1,z)] = -1
            kb = kb + 1
            
        i = kr
        if (kg < i): i = kg
        if (kb < i): i = kb
        if (silent==False):
            if ((i < m*n) and (i != i_prev)): pbar.update(1)
        i_prev = i
    
    if (silent==False):
        if (i <= (m*n)): pbar.update(1)
    if (silent==False): pbar.close()
    
    Id = []
    for i in range(m*n):
        Id.append((Ir[i], Ig[i], Ib[i]))
        
    return Id

#Function that displays the help message
def show_help(isError):
    "Displays the help message"
    "Input:"
    "isError: tells the function if it has been called from an exception or not"
    "Output:"
    "Sends the help message to stderr if 'isError' is True, and to stdout otherwise" 
    
    message = ""
    
    message += "imgcrypt: an RGB color image encryption/decryption scheme, using a pseudo-random number generator based on a novel 3D chaotic map.\n"
    message += "\n"
    message += "imgcrypt [options] -k key file\n"
    message += "\n"
    message += "-h, --help\t display this help and exit.\n"
    message += "-V, --version\t display version information and exit.\n"
    message += "-s, --silent\t mute all output.\n"
    message += "-l, --lossless\t save/read encrypted data in an alternative, lossless format.\n"
    message += "-e, --encrypt\t run in encrypt mode (default).\n"
    message += "-d, --decrypt\t run in decrypt mode.\n"
    message += "-u, --unhurried\t use the unoptimized version of the chaotic masks generation algorithm.\n"
    message += "\n"
    message += "-k, --key\t initial guess for encryption or key for decryption.\n"
    message += "\n"
    message += "imgcrypt -e -k \"0.411;0.321;0.631\" \"lena_std.tif\""
    
    if (isError == True):
        print("\n" + message, file=sys.stderr)
    else:
        print(message)

#Function that displays the program version
def show_version():
    "Sends the program version message contained in global variable 'version' to stdout" 
    
    message = ""
    
    message += version + "\n\n"
    message += "Based on \"A pseudo-random numbers generator based on a novel 3D chaotic map with an application to color image encryption\" by Mohamed Lamine Sahari & Ibtissem Boukemara (https://doi.org/10.1007/s11071-018-4390-z)\n\n"
    message += "Created by Juan Manuel Gonzalez (juanmg0511@gmail.com)\n"
    message += "FIUBA - 75.26 Simulación - 2c2019"

    print(message)

#Main function
def main():
    #All normal outputs are sent to stdout, can be suppressed using '-s' option
    #ERRORS and WARNINGS are sent to stderr and cannot be suppressed
    
    #Command line arguments parser
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hVsleduk:", ["help", "version", "silent", "lossless", "encrypt", "decrypt", "unhurried", "key"])
    except getopt.GetoptError as OptionError:
        print("ERROR: " + str(OptionError) + ".", file=sys.stderr)
        show_help(True)
        sys.exit(1)

    #Set options and program modes
    global silent
    global unhurried
    lossless = False
    mode = "e"
    key = ""
    path_original = ""
    path_final = ""
    for o, a in opts:
        if o in ("-h", "--help"):
            show_help(False)
            sys.exit(0)
        elif o in ("-V", "--version"):
            show_version()
            sys.exit(0)
        elif o in ("-s", "--silent"):
            silent = True
        elif o in ("-l", "--lossless"):
            lossless = True
        elif o in ("-e", "--encrypt"):
            mode = "e"
        elif o in ("-d", "--decrypt"):
            mode = "d"
        elif o in ("-u", "--unhurried"):
            unhurried = True
        elif o in ("-k", "--key"):
            key = a
        else:
            print("ERROR: unhandled option.", file=sys.stderr)
            show_help(True)
            sys.exit(1)

    #Validation of supplied intial guess/key
    if (key == ""):
        print("ERROR: Initial guess or key is required.", file=sys.stderr)
        show_help(True)
        sys.exit(1)
    else:
        Kd = key.split(";")
        if (len(Kd) != 3):
            print("ERROR: Initial guess or key format is invalid.", file=sys.stderr)
            show_help(True)
            sys.exit(1)  
        try:
            Kd = list(map(float,Kd))
        except:
            print("ERROR: Initial guess or key format is invalid.", file=sys.stderr)
            show_help(True)
            sys.exit(1)    
    
    #Validation of input file presence
    if (len(args) == 0):
        print("ERROR: Image path is required.", file=sys.stderr)
        show_help(True)
        sys.exit(1)
    else:
        path_original = args[0]
    
    #File name definition, with path, name and extension
    path_original_name, path_original_extension = os.path.splitext(path_original)
    path_encrypted = path_original_name
    path_encrypted_lossless = path_original_name
    path_decrypted = path_original_name
    if (path_original_extension == ""):
        path_encrypted += "_encrypted"
        path_encrypted_lossless += "_encrypted_lossless"
        path_decrypted += "_decrypted"
    else:
        path_encrypted += "_encrypted" + path_original_extension
        path_encrypted_lossless += "_encrypted_lossless" + path_original_extension
        path_decrypted += "_decrypted" + path_original_extension
    
    #Opening and validation of input file
    try:
        im_original = None
        if ((lossless==True) and (mode=="d")):
            #Read lossless format dictionary and impact data into Pillow
            im_original_data = pickle.load(open(path_original,"rb"))
            im_original = Image.new(mode=im_original_data["imageMode"], size=im_original_data["imageSize"])
            im_original.format = im_original_data["imageFormat"]
            im_original.putdata(im_original_data["imageData"])            
        else:
            #Read normally with Pillow
            im_original = Image.open(path_original)
        
        #Get the RGB values of each pixel in the original image, plus width and height
        Io = list(im_original.getdata())        
        n = im_original.width
        m = im_original.height            
    except Exception as FileOpenException:
        print("Error opening file \"" + path_original + "\": " + str(FileOpenException), file=sys.stderr)
        sys.exit(1)
    
    #Throw an error and exit if file is not RGB, scheme is specific to the RGB format
    #TODO: implement for al modes
    if (im_original.mode != "RGB"):
        print("ERROR: only RGB files are supported, file is \"" + im_original.mode + "\".", file=sys.stderr)
        sys.exit(1)

    #Display message on succesful read
    if (silent==False): print("Opened file \"" + path_original + "\", " + str(os.stat(path_original).st_size) + " bytes read.")
        
    #Warn the user if the selected file uses lossy compression and the non-lossless encryption mode is being used
    if (((str(im_original.format)).lower() in lossy_formats) and (mode=="e") and (lossless==False)):
        print("WARNING: file format uses lossy compression. Results may be unexpected, please use lossless '-l' flag.", file=sys.stderr)
    
    #Main processing
    if (mode=="e"): 
        #Encryption mode
        K, If = encryptImage(Kd, Io, m, n)   
        path_final = path_encrypted
        
        #Output the encryption key to stdout
        #These two sentences cannot be suppressed using silent mode, as the key is required to decrypt the file
        print("\nEncrypted image \"" + path_original + "\" with key K:")
        print(str(list(K)).replace(", ",";"))
        
    else:
        #Decryption mode
        If = decryptImage(Kd, Io, m, n)
        path_final = path_decrypted
        
        if (silent==False): print("\nDecrypted image \"" + path_original + "\" with key K:")
        if (silent==False): print(str(list(Kd)).replace(", ",";"))
     
    #Saving of the result file
    try:
        #Copies the final version of the file into an Image object
        im_final = Image.new(im_original.mode, im_original.size)
        im_final.putdata(If)
        #This version of the program, according to the original scheme, is not concerned with preserving/encrypting EXIF, or the image's color profile
        #TODO: save and encrypt EXIF - im_original.info.get("exif")
        #TODO: save and encrypt color profile - im_original.info.get("icc_profile")
        if ((lossless==False) or (mode=="d")):
            #Non-lossless mode, use Pillow
            im_final.save(path_final, format=im_original.format, quality="keep", subsampling="keep")
        else:
            #Lossless mode, generate a custom dictionary with the image data to be saved
            #TODO: compress dictionary to reduce size of dump
            path_final = path_encrypted_lossless
            im_original_data = {
                "imageFormat": im_original.format,
                "imageMode": im_original.mode,
                "imageSize": im_original.size,
                "imageData": If
            }
            #Dump data to file
            pickle.dump(im_original_data, open(path_encrypted_lossless,"wb"))
    except Exception as FileSaveException:
        print("Error saving file \"" + path_final + "\": " + str(FileSaveException), file=sys.stderr)
        sys.exit(1)

    #Display message on succesful save and end of excecution
    if (silent==False): print("\nSaved file \"" + path_final + "\", " + str(os.stat(path_final).st_size) + " bytes written.")
    if (silent==False): print("Done.")
        
    return (0)

#Call to main()
if __name__ == "__main__":
    main()
