:- use_module(library(clpfd)).
:- set_prolog_stack(global, limit(1 000 000 000)).

% (StaffID , Semester , Course , Tutorials , RoomType ,DaysOFF,RoomSlot )
%solve([(9,5,8,[4,5,6,7,8],1,[0,3,4],C0),(3,5,2,[9,10,11,12,13,14],1,[1,3,4],C1),(9,5,8,[9,10,11,12,13,14,15,16],1,[0,3,4],C2),(3,5,2,[4,5,6,7,8],1,[1,3,4],C3),(3,5,2,[9,10,11,12,13,14],1,[1,3,4],150),(3,5,2,[4,5,6,7,8],1,[1,3,4],151),(4,5,3,[15,16],1,[1,2,3,4],272),(5,5,4,[4,5,6,7,8],1,[0,3,4],395),(6,5,5,[4,5,6,7,8],1,[0,3,4],396),(7,5,7,[9,10,11,12,13,14,15,16],1,[3,4],276),(6,5,5,[9,10,11,12,13,14,15,16],1,[0,3,4],397),(8,5,6,[4,5,6,7,8],1,[0,2,3,4],398),(5,5,4,[9,10,11,12,13,14,15,16],1,[0,3,4],535),(8,5,6,[9,10,11,12,13,14,15,16],1,[0,2,3,4],536),(7,5,7,[4,5,6,7,8],1,[3,4],537)],[152,153,154,155,156,157,158,159,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,270,271,273,274,275,277,278,279,285,286,287,288,289,290,291,292,293,294,295,296,297,298,299,390,391,392,393,394,399,405,406,407,408,409,410,411,412,413,414,415,416,417,418,419,510,511,512,513,514,515,516,517,518,519,525,526,527,528,529,530,531,532,533,534,538,539,630,631,632,633,634,635,636,637,638,639,645,646,647,648,649,650,651,652,653,654,655,656,657,658,659],[82],[]).

solve(Schedules , FreeRooms , Preferable , NonPreferable):-
	get_RoomSlots_Var(Schedules , RoomSlots),
	free_room_constraint(RoomSlots , FreeRooms),
	all_distinct(RoomSlots),
	same_RoomType_constraint(Schedules),
	group_slot_constraint(Schedules),
	staff_slot_constraint(Schedules),
	calculatePrefrences(Schedules , Preferable , NonPreferable , Score),
	labeling([min(Score)] , RoomSlots).
			
same_RoomType_constraint(Schedules):- 
	get_RoomSlots(Schedules , RoomSlots) , get_RoomType(Schedules , RoomTypes) , 
	maplist(same_RoomType_compare , RoomSlots , RoomTypes , Check), 
	sum(Check, #=, Num),
	length(Schedules , Num).
	
group_slot_constraint(Schedules):- 
	get_hash_group_slot(Schedules , HashList), 
	all_distinct(HashList).

staff_slot_constraint(Schedules):- 
	get_hash_staff_slot(Schedules , HashList), 
	all_distinct(HashList).
	
free_room_constraint(RoomSlots , FreeRooms):- 
		all_in_List(RoomSlots , FreeRooms).
		
calculatePrefrences(Schedules ,Preferable , NonPreferable, Score):-
		calculatePrefrences_helper(Schedules , Preferable , 1 , Score1),
		calculatePrefrences_helper(Schedules , NonPreferable , 2 , Score2),
		calculate_days_off(Schedules  , Score3),
		Score #=  Score1 + Score2 + Score3.
		
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% HELPER Predicates %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
		
compare_preference((StaffID , Semester , Course , Tutorials , RoomType, DaysOFF, RoomSlot) , Pref , B) :- 
	Hash #= StaffID * 30 + (RoomSlot mod 30) , 
	Pref #= Hash #<==> B.

compare_days_off(RoomSlot , Day , B) :- 
	Hash #= (RoomSlot // 5)  mod 6 ,
	Day #= Hash #<==> B.

calculatePrefrences_helper([] , Prefrences, Factor , 0).

calculatePrefrences_helper([Schedule | T] , Prefrences, Factor , Score):-
	maplist(compare_preference(Schedule) , Prefrences , TotalCosts),
	sum(TotalCosts , #= , Cost), 
	calculatePrefrences_helper(T , Prefrences , Factor, Score1),
	Score #= Score1 + Cost * Factor.
	
calculate_days_off([] , 0).
calculate_days_off([Schedule | T]  , Score):- 
	Schedule = (StaffID , Semester , Course , Tutorials , RoomType, DaysOFF, RoomSlot), 
	maplist(compare_days_off(RoomSlot) , DaysOFF , TotalCosts),
	sum(TotalCosts , #= , Cost), 
	calculate_days_off(T  , Score1),
	Score #= Score1 + Cost * 3.

get_RoomSlots([] , []).
get_RoomSlots([(StaffID , Semester , Course , Tutorials , RoomType ,DaysOFF,RoomSlot ) | T] , [RoomSlot | L]):- 
		get_RoomSlots(T , L).

get_RoomSlots_Var([] , []).
get_RoomSlots_Var([(StaffID , Semester , Course , Tutorials , RoomType ,DaysOFF,RoomSlot ) | T] , [RoomSlot | L]):- 
		var(RoomSlot),get_RoomSlots_Var(T , L).
get_RoomSlots_Var([(StaffID , Semester , Course , Tutorials , RoomType ,DaysOFF,RoomSlot ) | T] , L):- 
		nonvar(RoomSlot),get_RoomSlots_Var(T , L).

get_RoomType([] , []).
get_RoomType([(StaffID , Semester , Course , Tutorials , RoomType ,DaysOFF,RoomSlot ) | T] , [RoomType | L]):-
	get_RoomType(T , L).

get_hash_group_slot([] , []).	
get_hash_group_slot([(StaffID , Semester , Course , Tutorials , RoomType ,DaysOFF,RoomSlot ) | T] , [Hash | L]):-
		Slot #= RoomSlot mod 30 , Hash #= Semester * 8 * 20 * 30 + Course * 20 * 30 + Tutorial * 30 + Slot,
		get_hash_group_slot(T , L).
get_hash_staff_slot([] , []).	
get_hash_staff_slot([(StaffID , Semester , Course , Tutorials , RoomType ,DaysOFF,RoomSlot ) | T] , [Hash | L]):-
	Slot #= RoomSlot mod 30 , Hash #= StaffID * 30 + Slot,
	get_hash_staff_slot(T , L).
			
same_RoomType_compare(RoomSlot , RoomType , B):- Z #= (RoomSlot // 30) mod 4 , Z #= RoomType #<==> B.	

all_in_List([] , L).
all_in_List([H | T] , L):- element(_,L , H) , all_in_List(T , L).