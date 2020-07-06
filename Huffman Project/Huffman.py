# Define node class of Huffman tree
class node(object):
	def __init__(self,value=None,left=None,right=None,sup=None):
		self.value = value
		self.left = left
		self.right = right
		self.sup = sup

	def con_sup(left,right):
		n = node(value = left.value + right.value,left = left,right = right)
		left.sup = right.sup = n
		return n

	def encode(n):
		if n.sup == None:
			return b''
		if n.sup.left == n:
			return node.encode(n.sup) + b'0'		#left node encode as '0'
		else:
			return node.encode(n.sup) + b'1'		#right node encode as '1'

#Construct the Huffman tree
def con_tree(tree):
	if len(tree) == 1:
		return tree
	sorts = sorted(tree,key = lambda x:x.value)
	n = node.con_sup(sorts[0],sorts[1])
	sorts.pop(0)
	sorts.pop(0)
	sorts.append(n)
	return con_tree(sorts)

# Output encoding table 
def encode(echo):
	for x in nd_dict.keys():
		ec_dict[x] = node.encode(nd_dict[x])
		if echo == True:						
			print(x,ec_dict[x])

# Define compressing method for files
def compfile(inputfile):
	print("Starting compress...")
	f = open(inputfile,"rb")		
	i = 0
	f.seek(0,2)
	count = f.tell()
	nodes = []
	cache = [b''] * int(count)
	f.seek(0)
	#Calculate character frequency and build a single character into a single node
	while i < count:
		cache[i] = f.read(1)
		if ct_dict.get(cache[i], -1) == -1:
			ct_dict[cache[i]] = 0
		ct_dict[cache[i]] = ct_dict[cache[i]] + 1
		i = i + 1
	print("Read finished")
	print(ct_dict)				#Output weight dictionary
	for x in ct_dict.keys():
		nd_dict[x] = node(ct_dict[x])
		nodes.append(nd_dict[x])	
	f.close()
	con_tree(nodes)		#Construct the Huffman tree
	encode(False)			#Construct the encoding table, set Ture to see encoding maps.
	print("Encoding table is OK")
	# Write the compressed binary file
	i = 0
	raw = 0b1
	end = 0
	name = inputfile.split('/')
	o = open(name[0]+".hm" , 'wb')
	o.write((name[len(name)-1] + '\n').encode(encoding="utf-8"))	#write the original file name
	o.write(int.to_bytes(len(ec_dict) ,2 ,byteorder = 'big'))		#wirte the number of nodes
	for x in ec_dict.keys():										#encode the file header
		o.write(x)
		o.write(int.to_bytes(ct_dict[x] ,3 , byteorder = 'big'))
	while i < count:												#Start compressing data
		for x in ec_dict[cache[i]]:
			raw = raw << 1
			if x == 49:
				raw = raw | 1
			if raw.bit_length() == 9:
				raw = raw & (~(1 << 8))
				o.write(int.to_bytes(raw ,1 , byteorder = 'big'))
				o.flush()
				raw = 0b1
				pro = int(i / count * 100)
				if pro > end:
					print("compressing:", pro ,'%')						#Output compressing progress
					end = pro
		i = i + 1
	o.close()
	print("File compress successful.")

# Define decompressing method for files
def decompfile(inputfile):
	print("Starting decompress...")
	count = 0
	raw = 0
	end = 0
	f = open(inputfile ,'rb')
	f.seek(0,2)
	eof = f.tell()
	f.seek(0)
	name = inputfile.split('/')
	outputfile = inputfile.replace(name[len(name)-1], f.readline().decode(encoding="utf-8"))
	o = open(outputfile.replace('\n','') ,'wb')
	count = int.from_bytes(f.read(2), byteorder = 'big')			#Take out the number of nodes
	i = 0
	de_dict = {}
	while i < count:												#Parsing file headers
		key = f.read(1)
		value = int.from_bytes(f.read(3), byteorder = 'big')
		de_dict[key] = value
		i = i + 1
	for x in de_dict.keys():
		nd_dict[x] = node(de_dict[x])
		nodes.append(nd_dict[x])
	con_tree(nodes)					#reconstruct Huffman tree
	encode(False)								#Create encoding table, set Ture to see encoding maps.
	for x in ec_dict.keys():					#Construct the reverse dictionary
		iv_dict[ec_dict[x]] = x
	i = f.tell()
	data = b''
	while i < eof:								#Start decompressing data
		raw = int.from_bytes(f.read(1), byteorder = 'big')
		i = i + 1
		j = 8
		while j > 0:
			if (raw >> (j - 1)) & 1 == 1:
				data = data + b'1'
				raw = raw & (~(1 << (j - 1)))
			else:
				data = data + b'0'
				raw = raw & (~(1 << (j - 1)))
			if iv_dict.get(data, 0) != 0:
				o.write(iv_dict[data])
				o.flush()
				data = b''
			j = j - 1
		pro = int(i / eof * 100)
		if pro > end:							
			print("decompressing:", pro,'%')			#Output decompression progress
			end = pro
		raw = 0
	f.close()
	o.close()
	print("File decompress successful.")

#init data
nd_dict = {}
ct_dict = {}
ec_dict = {}
iv_dict = {}
nodes = []

if input("Please choose what you want to do:\n1：Compression\t2：Decompression\n") == '1':
	compfile(input("Please input a file with path for compression:"))
else:
	decompfile(input("Please input a file with path for decompression:"))  