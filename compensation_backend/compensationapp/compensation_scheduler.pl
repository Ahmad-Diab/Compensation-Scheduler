:- use_module(library(clpfd)).

% (StaffID , Semester , Course , Tutorials , RoomType ,DaysOFF,RoomSlot )

solve(Schedules , FreeRooms , Preferable , NonPreferable , S):-
	get_RoomSlots_Var(Schedules , RoomSlots),
	free_room_constraint(Schedules , FreeRooms),
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
	
free_room_constraint(Schedules , FreeRooms):- 
		get_RoomSlots_Var(Schedules , RoomSlots),
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
	
get_schedule_var(Schedules , SchedulesVar):- 
	setof((StaffID , Semester , Course , Tutorials , RoomType ,DaysOFF , RoomSlot) , StaffID^Semester ^ Course^ Tutorials^ RoomType^ RoomSlot^DaysOFF^(member((StaffID , Semester , Course , Tutorials , RoomType ,DaysOFF , RoomSlot) , Schedules) , nonvar(RoomSlot)) , RoomSlots).
			
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