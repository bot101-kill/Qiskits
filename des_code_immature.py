import numpy as np
import random
#48 bit round key for des, here we use 6 bit
#64 bit input for des, but here i will take 8 bit input

def left_shift(array):
    left_temp=array[0]
    right_temp=array[4]
    for j in range(0,8):
        if j==3:
            array[j]=left_temp
        elif j==7:
            array[j]=right_temp
        else:
            array[j]=array[j+1]
    return array

class des:
 def function_f(array,key_array):
    #expansion of right array of 4 to 6bit
    relation={1:3,2:1,3:2,4:3,5:4,6:2}
    temp_array=np.zeros(6,dtype=int)
    for key,value in relation.items():
        temp_array[key-1]=array[value-1]
    #this temp array is ready for xor operation with key array called key whitening
    xor_array=np.zeros(6,dtype=int)
    for i in range(0,6):
        if temp_array[i]==key_array[i]:
            xor_array[i]=0
        else:
            xor_array[i]=1
    #now we have xor array
    #now we have to do sbox operation, but i am making it a bit costumised to introduce non linearity
    #sbox operation
    sbox_array=np.zeros(4,dtype=int)
    for i in range(2,6):
        sbox_array[i-2]=xor_array[i]*xor_array[i-1]
    #sbox array is ready
    #now we have to do permutation box operation , but it is un necessaary so skipping it
    return sbox_array

 def straight_permutation_box_1(array):
    #we can make a permutation table , but i would just do shifting type
    relation={1:5,2:3,3:8,4:6,5:1,6:7,7:2,8:4}    #key is input position , vlaue is output position
    temp_array=np.zeros(8,dtype=int)
    for key,value in relation.items():
        temp_array[value-1]=array[key-1]
    return temp_array
 
 def round(round_number,array,round_key_array):
    left_array=np.zeros(4,dtype=int)
    right_array=np.zeros(4,dtype=int)
    n=8 # input array size (7 by index)
    for i in range(0,4):
       left_array[i]=array[i]
       right_array[i]=array[int(n/2)+i]
    # left and right array are now ready for operation
    result_function_f=des.function_f(right_array,round_key_array)
    #xor with left array
    xor_array=np.zeros(4,dtype=int)
    for i in range(0,4):
        if left_array[i]==result_function_f[i]:
            xor_array[i]=0
        else:
            xor_array[i]=1
    #swapper
    temp_array=np.zeros(8,dtype=int)
    if round_number==16:
        for i in range(0,4):
         temp_array[int(n/2)+i]=right_array[i]
         temp_array[i]=xor_array[i]
    else:
      for i in range(0,4):
        temp_array[i]=right_array[i]
        temp_array[int(n/2)+i]=xor_array[i]
    return temp_array
    
 def straight_permutation_box_1_inverse(array):
    relation={1:5,2:3,3:8,4:6,5:1,6:7,7:2,8:4}    #key is input index , vlaue is output index of straight 1
    temp_array=np.zeros(8,dtype=int)
    for key,value in relation.items():
        temp_array[key-1]=array[value-1]
    return temp_array
 
 def round_keys_array_2d(key_array):
    #key array is 8 bit
    #key generation , parity drop nahi kar rahe 
    #now we have to do left shift
    output_array_2d=np.zeros((16,6),dtype=int)
    left_shift_array=key_array
    for i in range(0,16):
        if i==0 or i==1 or i==8 or i==15:
            left_shift_array=left_shift(left_shift_array)
        else:
            left_shift_array=left_shift(left_shift_array)
            left_shift_array=left_shift(left_shift_array)
        # print("key schedule before s box for round",i+1,"is",left_shift_array)

        comp_box_array=np.zeros(6,dtype=int)       #for 6 bit round key output, yha kyunki chota bit size h 
        for k in range(2,8):
            # comp_box_array[k-2]=random.randint(0,1)    #random number generation
            comp_box_array[k-2]=left_shift_array[k]    #as per ecb , no randomness
            
            
        print("key schedule for round number",i+1,"is",comp_box_array)
        output_array_2d[i]=comp_box_array

    return output_array_2d   #for inverse just choose output_array_2d[16+1-roundnumber]
 

#  def key_generation_inverse(key_array):
#     reverse_array=des.round_key_array_2d(key_array)
    
#     return reverse_array

#main function
input_array=np.array([1,1,1,0,1,0,0,1])
key_array=np.array([1,1,1,0,1,0,1,1])
round_key_array=des.round_keys_array_2d(key_array)

cipher_array=des.straight_permutation_box_1(input_array)
for i in range(0,16): 
    cipher_array=des.round(i+1,cipher_array,round_key_array[i])   
cipher_array=des.straight_permutation_box_1_inverse(cipher_array)

decipher_array=des.straight_permutation_box_1(cipher_array)

for i in range(0,16):
    decipher_array=des.round(i+1,decipher_array,round_key_array[15-i])

decipher_array=des.straight_permutation_box_1_inverse(decipher_array)
   
    

print(*input_array)
print(*cipher_array)
print(*decipher_array)


    

