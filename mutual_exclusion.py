import pywren_ibm_cloud as pywren
import time
import json
import ibm_boto3


BUCKET_NAME = 'bucket-enric'
N_SLAVES = 20
X = 1.01     #seconds

def clean():
    
    #Borrar tots els pwrite
    try:
        llistaPW = ibm_cos.list_objects_v2(Bucket=BUCKET_NAME, Prefix='p_write_{')
        for k in llistaPW['Contents']:
            ibm_cos.delete_object(Bucket=BUCKET_NAME, Key=k['Key'])
    except:
        time.sleep(0)


    #Borrar tots els write
    try:
        llistaW = ibm_cos.list_objects_v2(Bucket=BUCKET_NAME, Prefix='write_{')
        for k in llistaW['Contents']:
            ibm_cos.delete_object(Bucket=BUCKET_NAME, Key=k['Key'])
    except:
        time.sleep(0)

    #Borrar result.json
    try:
        ibm_cos.delete_object(Bucket=BUCKET_NAME,Key='result.json')
    except:
        time.sleep(0)



def master(x, ibm_cos):
    write_permission_list = []
    old_last_modified = ibm_cos.get_object(Bucket=BUCKET_NAME,Key='result.json')['LastModified']
    new_last_modified=old_last_modified

    while True:
    # 1. monitor COS bucket each X seconds
        time.sleep(X)
        try:
            # 2. List all "p_write_{id}" files
            resultat = ibm_cos.list_objects(Bucket=BUCKET_NAME, Prefix='p_write_{')['Contents']
        
        except:
            break

        # 3. Order objects by time of creation
        resultat = sorted(resultat, key=lambda x: x['LastModified'])
        # 4. Pop first object of the list "p_write_{id}"
        top=resultat.pop()
        # 5. Write empty "write_{id}" object into COS
        write=top['Key'].replace('p_','')
        ibm_cos.put_object(Body='', Bucket=BUCKET_NAME, Key=write)
        # 6. Delete from COS "p_write_{id}", save {id} in write_permission_list
        ibm_cos.delete_object(Bucket=BUCKET_NAME,Key=top['Key'])
        write_permission_list.append(top['Key'].replace('p_write_{','').replace('}',''))
        # 7. Monitor "result.json" object each X seconds until it is updated
        while (old_last_modified == new_last_modified):
            time.sleep(X)
            new_last_modified = ibm_cos.get_object(Bucket=BUCKET_NAME,Key='result.json')['LastModified']

        old_last_modified=new_last_modified

        # 8. Delete from COS “write_{id}”
        ibm_cos.delete_object(Bucket=BUCKET_NAME,Key=write)
        # 9. Back to step 1 until no "p_write_{id}" objects in the bucket
   
    return write_permission_list


def slave(id, x, ibm_cos):
    # 1. Write empty "p_write_{id}" object into COS
    ibm_cos.put_object(Body='', Bucket=BUCKET_NAME, Key='p_write_{'+str(id)+'}')
    # 2. Monitor COS bucket each X seconds until it finds a file called "write_{id}"
    time.sleep(X)
    while True:
        try:
            ibm_cos.head_object(Bucket=BUCKET_NAME, Key='write_{'+str(id)+'}')
            break
        except:
            time.sleep(X)

    
    # 3. If write_{id} is in COS: get result.json, append {id}, and put back to COS result.json
    result = json.loads(ibm_cos.get_object(Bucket=BUCKET_NAME,Key='result.json')['Body'].read())
    result.append(str(id))
    ibm_cos.put_object(Body=json.dumps(result), Bucket=BUCKET_NAME, Key='result.json')
    # 4. Finish
    # No need to return anything

if __name__ == '__main__':
    pw = pywren.ibm_cf_executor()
    ibm_cos = pw.internal_storage.get_client()
    
    #Clean de tots els fitxers
    clean()

    ibm_cos.put_object(Body=json.dumps([]), Bucket=BUCKET_NAME, Key='result.json')
    start_time = time.time()

    pw.map(slave, range(N_SLAVES))
    pw.call_async(master, 0)
    write_permission_list = pw.get_result()

    elapsed_time = time.time() - start_time
    print(elapsed_time)

    # Get result.json
    result = json.loads(ibm_cos.get_object(Bucket=BUCKET_NAME,Key='result.json')['Body'].read())
    
    # check if content of result.json == write_permission_list
    if result == write_permission_list:
        print("Execució correcta. Les llistes són iguals:")
        print('result.json:\n'+str(result))
        print('write_permission_list:\n'+str(write_permission_list))
    else:
        print("Execució incorrecta. Les llistes no són iguals:")
        print('result.json:\n'+str(result))
        print('write_permission_list:\n'+str(write_permission_list))
    
    #Clean de tots els fitxers
    clean()
    