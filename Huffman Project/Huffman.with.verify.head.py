#Define the node class of Huffman tree
class node(object):

	def __init__(self,value=None,left=None,right=None,father=None):
		self.value = value
		self.left = left
		self.right = right
		self.father = father

	def build_father(left,right):
		n = node(value = left.value + right.value,left = left,right = right)
		left.father = right.father = n
		return n

	def encode(n):
		if n.father == None:
			return b''
		if n.father.left == n:
			return node.encode(n.father) + b'0'		#left node encode as '0'
		else:
			return node.encode(n.father) + b'1'		#right node encode as '1'

#Construct the Huffman tree
def build_tree(tree):
	if len(tree) == 1:
		return tree
	sorts = sorted(tree,key = lambda x:x.value,reverse = False)
	n = node.build_father(sorts[0],sorts[1])
	sorts.pop(0)
	sorts.pop(0)
	sorts.append(n)
	return build_tree(sorts)

# Output encoding table 
def encode(echo):

	for x in node_dict.keys():
		ec_dict[x] = node.encode(node_dict[x])
		if echo == True:						
			print(x)
			print(ec_dict[x])

def encodefile(inputfile):

	print("Starting encode...")
	f = open(inputfile,"rb")
	bytes_width = 1					
	i = 0

	f.seek(0,2)
	count = f.tell() / bytes_width
	print(count)
	nodes = []							#List of nodes, used to build the Huffman tree
	buff = [b''] * int(count)
	f.seek(0)

	#Calculate character frequency and build a single character into a single node
	while i < count:
		buff[i] = f.read(bytes_width)
		if count_dict.get(buff[i], -1) == -1:
			count_dict[buff[i]] = 0
		count_dict[buff[i]] = count_dict[buff[i]] + 1
		i = i + 1
	print("Read OK")
	print(count_dict)				#Output weight dictionary
	for x in count_dict.keys():
		node_dict[x] = node(count_dict[x])
		nodes.append(node_dict[x])
	
	f.close()
	build_tree(nodes)		#Construct the Huffman tree
	encode(False)					#Construct the encoding table
	print("Encode OK")

	head = sorted(count_dict.items(),key = lambda x:x[1] ,reverse = True)	#Sort all root nodes
	bit_width = 1
	print("head:",head[0][1])					#Dynamically adjust the byte width of the encoding table to optimize the file header size
	if head[0][1] > 255:
		bit_width = 2
		if head[0][1] > 65535:
			bit_width = 3
			if head[0][1] > 16777215:
				bit_width = 4
	print("bit_width:",bit_width)
	i = 0
	raw = 0b1
	last = 0
	name = inputfile.split('.')
	o = open(name[0]+".hm" , 'wb')
	name = inputfile.split('/')
	o.write((name[len(name)-1] + '\n').encode(encoding="utf-8"))	#write the original file name
	o.write(int.to_bytes(len(ec_dict) ,2 ,byteorder = 'big'))		#wirte the number of nodes
	o.write(int.to_bytes(bit_width ,1 ,byteorder = 'big'))			#write the encoding table's byte width
	for x in ec_dict.keys():										#encode the file header
		o.write(x)
		o.write(int.to_bytes(count_dict[x] ,bit_width ,byteorder = 'big'))

	print('head OK')
	while i < count:												#Start compressing data
		for x in ec_dict[buff[i]]:
			raw = raw << 1
			if x == 49:
				raw = raw | 1
			if raw.bit_length() == 9:
				raw = raw & (~(1 << 8))
				o.write(int.to_bytes(raw ,1 , byteorder = 'big'))
				o.flush()
				raw = 0b1
				tem = int(i  /len(buff) * 100)
				if tem > last:
					print("encode:", tem ,'%')						#Output compressing progress
					last = tem
		i = i + 1

	if raw.bit_length() > 1:										#Handle data with less than one byte at the end of the file
		raw = raw << (8 - (raw.bit_length() - 1))
		raw = raw & (~(1 << raw.bit_length() - 1))
		o.write(int.to_bytes(raw ,1 , byteorder = 'big'))
	o.close()
	print("File encode successful.")

def decodefile(inputfile):

	print("Starting decode...")
	count = 0
	raw = 0
	last = 0
	f = open(inputfile ,'rb')
	f.seek(0,2)
	eof = f.tell()
	f.seek(0)
	name = inputfile.split('/')
	outputfile = inputfile.replace(name[len(name)-1], f.readline().decode(encoding="utf-8"))
	o = open(outputfile.replace('\n','') ,'wb')
	count = int.from_bytes(f.read(2), byteorder = 'big')			#Take out the number of nodes
	bit_width = int.from_bytes(f.read(1), byteorder = 'big')		#Take out the code table word width
	i = 0
	de_dict = {}
	while i < count:												#Parsing file headers
		key = f.read(1)
		value = int.from_bytes(f.read(bit_width), byteorder = 'big')
		de_dict[key] = value
		i = i + 1
	for x in de_dict.keys():
		node_dict[x] = node(de_dict[x])
		nodes.append(node_dict[x])
	build_tree(nodes)					#reconstruct Huffman tree
	encode(False)								#Create encoding table
	for x in ec_dict.keys():					#Construct the reverse dictionary
		inverse_dict[ec_dict[x]] = x
	i = f.tell()
	data = b''
	while i < eof:								#Start decompressing data
		raw = int.from_bytes(f.read(1), byteorder = 'big')
		# print("raw:",raw)
		i = i + 1
		j = 8
		while j > 0:
			if (raw >> (j - 1)) & 1 == 1:
				data = data + b'1'
				raw = raw & (~(1 << (j - 1)))
			else:
				data = data + b'0'
				raw = raw & (~(1 << (j - 1)))
			if inverse_dict.get(data, 0) != 0:
				o.write(inverse_dict[data])
				o.flush()
				#print("decode",data,":",inverse_dict[data])
				data = b''
			j = j - 1
		tem = int(i / eof * 100)
		if tem > last:							
			print("decode:", tem,'%')			#Output decompression progress
			last = tem
		raw = 0

	f.close()
	o.close()
	print("File decode successful.")

if __name__ == '__main__':

	#init data
	node_dict = {}
	count_dict = {}
	ec_dict = {}
	nodes = []
	inverse_dict = {}

	if input("This is a python program for the Huffman encoding and decoding.\nPlease choose what you want to do:\n1：Compression\t2：Decompression\n") == '1':
		encodefile(input("Please input a file with path to compress:"))
	else:
		decodefile(input("Please input a file with path to decompress:"))  