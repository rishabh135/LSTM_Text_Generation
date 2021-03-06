import os
from keras.models import Sequential
from  keras.layers import Dense, Activation
from keras.layers import LSTM , GRU
#from keras.layers.recurrent import Sigmoid
from keras.layers.embeddings import Embedding
from keras.optimizers import RMSprop
import numpy as np
import os
#from tqdm import tqdm
import string

current_folder_path, current_folder_name = os.path.split(os.getcwd())
dfile = current_folder_path + '/data/t8.shakespeare.txt'

print (dfile)
with open (dfile,'r') as file:
	raw = file.read()

lowers = string.ascii_lowercase
k = set(raw.lower()) - set(lowers)
''.join(sorted(k))

extra = "\n !?';,."
allowed  = set(lowers + extra )
from collections import Counter , defaultdict
from string import maketrans
D = dict([(k,k) if k in allowed else(k," ") for k in set(raw.lower())])

keys = ''.join(D.keys())
vals = ''.join([D[i] for i in keys])
DD = maketrans(keys,vals)
data = raw.lower().translate(DD)

#collect repeated spaces and newlines
while '  ' in data:
	data = data.replace('  ',' ')

while '\n\n' in data:
	data = data.replace('\n\n','\n')

while '\n \n' in data:
	data = data.replace('\n \n','\n')

chars = list(lowers+extra)

print('  ' in data)
print (set(data) == allowed)
chars = sorted(list(set(data)))

#change unroll length
maxlen = 20
step =1
char_indices = dict((c,i) for i,c in enumerate(chars))
indices_char = dict((i,c) for i,c in enumerate(chars))

print("Building the model of a single LSTM")
model = Sequential()
#add embeddings
print("Adding embeddings")
print ("As we are in a space of 34 we reduce them to 16 dimensional real value spacings")
model.add(Embedding(len(chars),16,input_length=maxlen))
model.add(LSTM(32))
model.add(Dense(len(chars)))
model.add(Activation('softmax'))

# optimizer = RMSprop(lr = 0.01)
model.compile(loss = 'categorical_crossentropy' , optimizer = 'adadelta' , metrics = ['accuracy'])

epochs = 10
num_blocks = 10

# no one hot required for embeddings
# model.fit(X,Y,epochs=1,validation_split = 0.1)
# model.save_weights('bardic_weights_{0}.h5'.format(j))


# maybe not required
print("Truncating the data and reshaping it")
data = data[:-(len(data)%num_blocks)]
data = np.array(list(data)).reshape([num_blocks,-1])
from tqdm import tqdm



for j in tqdm(range(epochs)):
	for b in tqdm(range(num_blocks)):
		sentences = []
		next_chars = []
		for i in range(0,len(data[b]) -maxlen,step):
			sentences.append(data[b,i:i+maxlen])
			next_chars.append(data[b,i+maxlen])
		#encode all in one-hot representations or stick with dense encodings
		X = np.zeros([len(sentences),maxlen],dtype = np.uint8)
		Y = np.zeros([len(sentences),len(chars)],dtype= np.uint8)
		i = 0
		for t,char in enumerate(sentences[0]):
			X[i,t] = char_indices[char]
			Y[i,char_indices[next_chars[i]]] =1
		for i , sentence in enumerate(sentences[1:]):
			X[i+1,:-1] = X[i, 1:]
			X[i+1 , -1] = char_indices[next_chars[i]]
			Y[i+1 , char_indices[next_chars[i+1]]] = 1
		model.fit(X,Y,epochs=1,validation_split = 0.1)
	model.save_weights('bardic_weights_{0}.h5'.format(j))


# model.fit(X,Y,nb_epoch=10)
model.save_weights('final_bardic_weights.h5')
model.load_weights('final_bardic_weights.h5')

class Bard(object):
	"""docstring for Bard"""
	def __init__(self,model ,primer = 'the quick brown fox jumped over the lazy fox', maxlen = 20 , numchar = 34 , chars = char, diversity = 0.5):
		super(Bard, self).__init__()
		self.model = model
		seld.text = primer[-maxlen:].lower()
		assert set(self.text).issubset(set(chars))
		self.diversity = diversity
		self.chars = chars
		self.onehot = np.zeros([1,maxlen,numchar],dtype = np.uints8)
		for i,p in enumerate(primer[::-1]):
			self.onehot[0,maxlen-i-1,self.chars.index(p)]=1
		self.dense  = np.argmax(self.onehot,axis=2)

	def sample(self,probs,diversity = 0.5):
		probs = np.asarray(probs).astype('float64')
		exp_preds = np.exp(np.log(probs)/diversity)
		preds = exp_preds/ sum(exp_preds)
		probas = np.random.multinomial(1,preds,1)
		return np.argmax(probas)

	def steps(self,n=1,verbose = True):
		for i in range(n):
			probs = model.predict(self.dense)[0]
			idx = self.sample(probs,self.diversity)
			self.text  += self.chars[idx]
			self.onehot[0,:-1] = self.onehot[0,1:]
			self.onehot[0,-1] = 0
			self.onehot[0,-1,self.chars.index(self.text[-1])] = 1
			self.dense = np.argmax(self.onehot , axis=2)
		if (verbose):
			print(self.text)

def test_model_with():
	b1 = Bard()
	b1.step(40,verbose=True)
	b2 = Bard(model,primer = ''.join(data[0,1000:1040]))
	b2.step(10)
	b2.step(100)


print("Do you want to test the model ? Press Y or y to do so , otehrwise press anything else to exit")
str1 = raw_input()
if(str1 == 'Y' or str1 =='y')
	test_model_with()

		