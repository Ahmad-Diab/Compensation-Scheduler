:- use_module(library(clpfd)).

% (StaffID , Semester , Course , Tutorials , RoomType ,DaysOFF,RoomSlot , Score)

solve(Schedules , FreeRooms , Preferable , NonPreferable):-
	free_room_constraint(Schedules , FreeRooms),
	same_RoomType_constraint(Schedules),
	group_slot_constraint(Schedules),
	staff_slot_constraint(Schedules),
	get_RoomSlots(Schedules , RoomSlots),
	all_distinct(RoomSlots),
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
	
free_room_constraint(Schedules , FreeRooms):- 
		get_RoomSlots_Var(Schedules , RoomSlots),
		all_in_List(RoomSlots , FreeRooms).
		
calculatePrefrences(Schedules ,Preferable , NonPreferable, Score):-
		calculate_preferable(Schedules , Preferable , Score1),
		calculate_non_preferable(Schedules , NonPreferable , Score2),
		calculate_not_mentioned(Schedules , Preferable , NonPreferable , Score3),
		calculate_days_off(Schedules ,Score4) , 
		Score #= Score1 + Score2 + Score3 + Score4.
		
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% HELPER Predicates %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%Preferable%%
calculate_preferable([] , Preferable , 0).
calculate_preferable([(StaffID , _ , _ , _ , _ ,_,RoomSlot) | T] , Preferable, Score):-
	Slot #= RoomSlot mod 30 , 
	Hash #= StaffID * 200 + Slot , 
	element(_,Preferable , Hash),
	calculate_preferable(T , Preferable , Score1),
	Score #= Score1 + 1.
calculate_preferable([(StaffID , _ , _ , _ , _ ,_,RoomSlot) | T] , Preferable, Score):-
	Slot #= RoomSlot mod 30 , 
	Hash #= StaffID * 200 + Slot , 
	\+ element(_,Preferable , Hash),
	calculate_preferable(T , Preferable , Score).
	

calculate_not_mentioned([] ,Preferable, NonPreferable , 0).
calculate_not_mentioned([(StaffID , _ , _ , _ , _ ,_,RoomSlot) | T]  , Preferable, NonPreferable, Score):-
	Slot #= RoomSlot mod 30 , 
	Hash #= StaffID * 200 + Slot , 
	(element(_,NonPreferable , Hash); element(_ , Preferable , Hash)),
	calculate_not_mentioned(T , Preferable, NonPreferable , Score).

calculate_not_mentioned([(StaffID , _ , _ , _ , _ ,_,RoomSlot) | T]  , Preferable, NonPreferable, Score):-
	Slot #= RoomSlot mod 30 , 
	Hash #= StaffID * 200 + Slot , 
	\+ element(_,NonPreferable , Hash), \+ element(_ , Preferable , Hash),
	calculate_not_mentioned(T ,Preferable, NonPreferable , Score1),
	Score #= Score1 + 2.

calculate_non_preferable([] , NonPreferable , 0).
calculate_non_preferable([(StaffID , _ , _ , _ , _ ,_,RoomSlot) | T] , NonPreferable, Score):-
	Slot #= RoomSlot mod 30 , 
	Hash #= StaffID * 200 + Slot , 
	\+ element(_,NonPreferable , Hash),
	calculate_non_preferable(T , NonPreferable , Score).
	
calculate_non_preferable([(StaffID , _ , _ , _ , _ ,_,RoomSlot) | T] , NonPreferable, Score):-
	Slot #= RoomSlot mod 30 , 
	Hash #= StaffID * 200 + Slot , 
	element(_,NonPreferable , Hash),
	calculate_non_preferable(T , NonPreferable , Score1),
	Score #= Score1 + 3.
	
calculate_days_off([] , 0).
calculate_days_off([(_ , _ , _ , _ , _ ,DaysOFF,RoomSlot) | T] , Score):- 
		Day #= (RoomSlot // 5)  mod 6, 
		element(_ ,DaysOFF , Day) , 
		calculate_days_off(T , Score1) , 
		Score #= Score1 + 4. 
calculate_days_off([(_ , _ , _ , _ , _ ,DaysOFF,RoomSlot) | T] , Score):- 
		Day #= (RoomSlot // 5)  mod 6, 
		\+ element(_ ,DaysOFF , Day) , 
		calculate_days_off(T , Score). 
		
get_RoomSlots(Schedules , RoomSlots):- 
	bagof(RoomSlot , StaffID^Semester ^ Course^ Tutorials^ RoomType^ RoomSlot^DaysOFF^ member((StaffID , Semester , Course , Tutorials , RoomType, DaysOFF, RoomSlot) , Schedules), RoomSlots).

get_RoomSlots_Var(Schedules , RoomSlots):- 
	bagof(RoomSlot , StaffID^Semester ^ Course^ Tutorials^ RoomType^ RoomSlot^DaysOFF^(member((StaffID , Semester , Course , Tutorials , RoomType ,DaysOFF , RoomSlot) , Schedules) , var(RoomSlot)) , RoomSlots).

get_RoomType(Schedules , RoomTypes):- 
	bagof(RoomType , StaffID^Semester ^ Course^ Tutorials^ RoomType^ RoomSlot^DaysOFF^ member((StaffID , Semester , Course , Tutorials , RoomType , DaysOFF, RoomSlot) , Schedules), RoomTypes).

get_hash_group_slot(Schedules , GroupSlotHash):- 
	bagof(Hash , StaffID^Semester ^ Course^ Tutorials^ RoomType^ RoomSlot^Tutorial^Hash^Slot^DaysOFF^(member((StaffID , Semester , Course , Tutorials , RoomType ,DaysOFF, RoomSlot) , Schedules) , member(Tutorial , Tutorials), Slot #= RoomSlot mod 30 , Hash #= Semester * 8 * 20 * 30 + Course * 20 * 30 + Tutorial * 30 + Slot) , GroupSlotHash).
		
get_hash_staff_slot(Schedules , StaffSlotHash):- 
	bagof(Hash , StaffID^Semester ^ Course^ Tutorials^ RoomType^ DaysOFF^ RoomSlot^Tutorial^Hash^Slot^(member((StaffID , Semester , Course , Tutorials , RoomType ,DaysOFF, RoomSlot), Schedules), Slot #= RoomSlot mod 30 , Hash #= StaffID * 200 + Slot) , StaffSlotHash).
		
same_RoomType_compare(RoomSlot , RoomType , B):- Z #= (RoomSlot // 30) mod 4 , Z #= RoomType #<==> B.	

all_in_List([] , L).
all_in_List([H | T] , L):- element(_,L , H) , all_in_List(T , L).