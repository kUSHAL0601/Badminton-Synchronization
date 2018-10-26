import threading
import time

entrance_gate=threading.Semaphore(value=1)
organizer=threading.Semaphore(value=1)
read_ready_arrays=threading.Semaphore(value=1)
player_threads=[]
refree_threads=[]
ready_players=[]
ready_refree=[]
done_with=[]

cnd=threading.Condition()
conditions={}


def warmup(id):
	print(id,"warming up")
	time.sleep(1)

def adjustEquipment(id):
	print(id,"adjusting equipments")
	time.sleep(0.5)


def enterAcademy(id):
	if(entrance_gate.acquire()):
		print(id,"entering at time",time.ctime(time.time()))
		entrance_gate.release()

def meetOrganizer(id):
	if(organizer.acquire()):
		print(id,"meeting organizer at time",time.ctime(time.time()))
		organizer.release()
		# if(read_ready_arrays.acquire()):
		ready_players.append(id)
			# read_ready_arrays.release()
			# print("Not releasing",id)

def ref_meetOrganizer(id):
	if(organizer.acquire()):
		print(id,"meeting organizer at time",time.ctime(time.time()))
		organizer.release()
		# if(read_ready_arrays.acquire()):
		ready_refree.append(id)
			# read_ready_arrays.release()
			# print("Not releasing",id)


def enterCourt(id):
	print(id,"tries to enter court")
	# warmup is included here only
	conditions[id].acquire()
	conditions[id].wait()
	print(id,"wait over")
	done_with.append(id)
	if id==ready_players[0]:
		# t1=Thread(target=warmup,args=(ready_players[0]))
		# t1.start()
		organizer.acquire()
		t1=Thread( target=warmup, args=(ready_players[0],) )
		t2=Thread( target=warmup, args=(ready_players[1],) )
		t3=Thread( target=adjustEquipment, args=(ready_refree[0],) )
		t3.start()
		t1.start()
		t2.start()
		t1.join()
		t2.join()
		t3.join()
		# if organizer.acquire():
		print("Starting game between",ready_players[0],ready_players[1],"under refree",ready_refree[0],"at time",time.ctime(time.time()))
		organizer.release()
		time.sleep(2) # Not specified still 2s time added for game
		print("Game between",ready_players[0],ready_players[1],"under refree",ready_refree[0],"ended",time.ctime(time.time()))
		p=ready_players.pop(0)
		print("Player",p,"leaving")
		p=ready_players.pop(0)
		print("Player",p,"leaving")
		r=ready_refree.pop(0)
		print("Refree",r,"leaving")
	else:
		print(id,"Waiting 2")

class playerThread (threading.Thread):
   def __init__(self, threadID):
      threading.Thread.__init__(self)
      self.threadID = "P"+str(threadID)
   def run(self):
      print ("Starting " + self.threadID)
      enterAcademy(self.threadID)
      meetOrganizer(self.threadID)
      enterCourt(self.threadID)
      print(self.threadID,"exiting")

class refreeThread (threading.Thread):
   def __init__(self, threadID):
      threading.Thread.__init__(self)
      self.threadID = "R"+str(threadID)
   def run(self):
      print ("Starting " + self.threadID)
      enterAcademy(self.threadID)
      ref_meetOrganizer(self.threadID)
      conditions[self.threadID].acquire()
      conditions[self.threadID].wait()
      print(self.threadID,"exiting")


from random import randint
from threading import Thread

def main():
	n=5
	tot=0
	id_player=0
	id_ref=0
	while (tot<3*n):
		tot+=1
		if(id_ref>=id_player//2):
			id_player+=1
			pt=playerThread(id_player)
			player_threads.append(pt)
			conditions[pt.threadID]=threading.Condition()
			pt.start()
		else:
			id_ref+=1
			rf=refreeThread(id_ref)
			refree_threads.append(rf)
			conditions[rf.threadID]=threading.Condition()
			rf.start()
		if(len(ready_players)>=2 and len(ready_refree)>=1):
			print(ready_players[0],ready_players[1],ready_refree[0])
			if(ready_players[0] not in done_with):
				conditions[ready_players[0]].acquire()
				conditions[ready_players[0]].notify()
				conditions[ready_players[0]].release()
				conditions[ready_players[1]].acquire()
				conditions[ready_players[1]].notify()
				conditions[ready_players[1]].release()
				conditions[ready_refree[0]].acquire()
				conditions[ready_refree[0]].notify()
				conditions[ready_refree[0]].release()
		time.sleep(randint(0,999)%3)
	player_threads[2*n-1].join()
	player_threads[2*n-2].join()
# class mainThread (threading.Thread):
#    def __init__(self):
#       threading.Thread.__init__(self)
#    def run(self):
#       print ("Starting Main Thread")
#       main()
#       print ("Exiting Main Thread")
t=Thread(target=main)
t.start()