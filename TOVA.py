import pandas as pd
import streamlit as st
import numpy as np
from st_aggrid import AgGrid
import scipy.io
import xlsxwriter
import io

ind=['reV','reT','com','omm','dpr']

st.title("NCI TOVA Converter")

penguin_file = st.file_uploader("Note: please select summary file *.iqdat", type=['iqdat'])
if penguin_file:
	kk = pd.read_csv(penguin_file, delimiter='\t')
	response=AgGrid(kk, height=100)
	#st.write(penguin_file)

col1,col2,col3=st.columns((2,1,1))

with col1:
	age=st.number_input(label='please enter age', min_value=4.0, max_value=200., value=199.)	

with col2:
	gender=st.radio("Gender",('Male','Female'))

with col3:
	modd=st.radio("Modality",('vis','aud'))
st.write("Note: age should be xx.x (must include decimal, precision is not important). For example, for 15 years 4 months old boy, the results for age 15.1 and 15.9 are the same.")
st.write("Note: for visual TOVA, 4 < age (4.1 is ok)")
st.write("Note: for auditory TOVA, 6 < age < 30 (6.1 is ok)")

if penguin_file is None:
	st.stop()

ttt2=np.empty((5,3))
ttt1=['varRT_Lo_Hi_All','meanRT_Lo_Hi_All','commission_Lo_Hi_All','omission_Lo_Hi_All','dprime_Lo_Hi_All']

mat=scipy.io.loadmat('TOVA_NCI.mat')

for i in range(5):
	tmp3=modd + '_' + str(ind[i])
	tmp=mat[tmp3]

	tmp3=modd + '_' + 'age'	            
	tmp1=mat[tmp3]

	tmp2=np.nonzero(tmp1>age) # get index	
	tmp2=tmp2[1][0]

	tmp2=tmp2-1 # the age index: 0 or 1 or 2 or 3 ...
	tmp2=tmp2*2	# the data index: 0 or 2 or 4 or 6 ...

	if gender == 'Female':
		tmp2=tmp2+1

	tmp2=tmp[tmp2,:] # extract the data                

	tt=[]
	if i == 0:
		tt=(kk['expressions.SDHitRT_LF'], kk['expressions.SDHitRT_HF'], kk['expressions.SDHitRT']);		
	elif i == 1:
		tt=(kk['expressions.meanHitRT_LF'], kk['expressions.meanHitRT_HF'], kk['expressions.meanHitRT'])
	elif i == 2:
		tt=(kk['expressions.commissionRate_LF'], kk['expressions.commissionRate_HF'], kk['expressions.commissionRate'])
	elif i == 3:
		tt=(kk['expressions.omissionsRate_LF'], kk['expressions.omissionsRate_HF'], kk['expressions.omissionsRate'])
	else:
		tt=(kk['expressions.dprime_LF'], kk['expressions.dprime_HF'], kk['expressions.dprime'])
    
	ttt2[i,:] = np.divide(np.diagonal(np.array(tt)-np.take(tmp2,[0,2,4])),np.take(tmp2,[1,3,5]))

st.subheader("Results: 1st half -> 2nd half -> overall")

ttt2=np.around(ttt2,4)

df1=pd.DataFrame(ttt2,columns=['1st half','2nd half','overall'], index=ttt1)

ACS=-1*ttt2[1,0]+ttt2[4,1]-ttt2[0,2]+1.8
ACS=np.around(ACS,4)
df2=pd.DataFrame([[ACS, '', '']],columns=['1st half','2nd half','overall'], index=["ACS"])

df1=df1.append(df2)

st.dataframe(df1)

out_path=penguin_file.name[0:-6] + '_Zscore.xlsx'

writer = pd.ExcelWriter(out_path,engine="xlsxwriter")
df1.to_excel(writer,sheet_name="Sheet1",index=True, header=False)

workbook = writer.book
worksheet = writer.sheets['Sheet1']
worksheet.autofit()

writer.save()
# writer.close()

# with pd.ExcelWriter(out_path,engine="xlsxwriter") as writer:
# 	df1.to_excel(writer,sheet_name="Sheet1",index=True, header=False)
# 	writer.save()
