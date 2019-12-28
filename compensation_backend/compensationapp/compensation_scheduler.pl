:- use_module(library(clpfd)).
:- set_prolog_stack(global, limit(1 000 000 000)).

solve(Schedules , FreeRooms , Preferable , NonPreferable):- %(StaffID , Semester , Course , Tutorials , RoomType ,DaysOFF,E)
	get_RoomSlots_Var(Schedules , E), 
	E ins 0 .. 5999,
	free_room_constraint(E , FreeRooms), 
	all_distinct(E),
	same_RoomType_constraint(Schedules),
	group_slot_constraint(Schedules),
	staff_slot_constraint(Schedules),
	calculatePrefrences(Schedules , Preferable , NonPreferable , Cost),
	labeling([min(Cost)] , E).

same_RoomType_constraint(Schedules):- 
	get_RoomSlots(Schedules , E) , get_RoomType(Schedules , RoomTypes) , 
	maplist(same_RoomType_compare , E , RoomTypes , Check), 
	sum(Check, #=, Num),
	length(Schedules , Num).
	
group_slot_constraint(Schedules):- 
	get_hash_group_slot(Schedules , HashList), 
	all_distinct(HashList).

staff_slot_constraint(Schedules):- 
	get_hash_staff_slot(Schedules , HashList), 
	all_distinct(HashList).
	
free_room_constraint(Es , FreeRooms):- 
		all_in_free_rooms(Es , FreeRooms).
		
calculatePrefrences(Schedules ,Preferable , NonPreferable, Cost):-
		calculatePrefrences_helper(Schedules , Preferable , 1 , Score1),
		calculatePrefrences_helper(Schedules , NonPreferable , 2 , Score2),
		calculate_days_off(Schedules  , Score3),
		Cost #=  Score1 + Score2 + Score3.
		
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% HELPER Predicates %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
		
compare_preference((StaffID , _ , _ , _ , _ ,_,E) , Pref , B) :- 
	Hash #= StaffID * 30 + (E mod 30) , 
	Pref #= Hash #<==> B.

compare_days_off(E , Day , B) :- 
	Hash #= (E // 5)  mod 6 ,
	Day #= Hash #<==> B.

calculatePrefrences_helper([] , _, _ , 0).

calculatePrefrences_helper([Schedule | T] , Prefrences, Factor , Score):-
	maplist(compare_preference(Schedule) , Prefrences , TotalCosts),
	sum(TotalCosts , #= , Cost), 
	calculatePrefrences_helper(T , Prefrences , Factor, Score1),
	Score #= Score1 + Cost * Factor.
	
calculate_days_off([] , 0).
calculate_days_off([Schedule | T]  , Score):- 
	Schedule = (_ , _ , _ , _ , _ ,DaysOFF,E), 
	maplist(compare_days_off(E) , DaysOFF , TotalCosts),
	sum(TotalCosts , #= , Cost), 
	calculate_days_off(T  , Score1),
	Score #= Score1 + Cost * 3.

get_RoomSlots([] , []).
get_RoomSlots([(_ , _ , _ , _ , _ ,_,E) | T] , [E | L]):- 
	get_RoomSlots(T , L).

get_RoomSlots_Var([] , []).
get_RoomSlots_Var([(_ , _ , _ , _ , _ ,_,E) | T] , [E | L]):- 
	var(E),get_RoomSlots_Var(T , L).
get_RoomSlots_Var([(_ , _ , _ , _ , _ ,_,E) | T] , L):- 
	nonvar(E),get_RoomSlots_Var(T , L).

get_RoomType([] , []).
get_RoomType([(_ , _ , _ , _ , RoomType ,_,_) | T] , [RoomType | L]):-
	get_RoomType(T , L).

get_hash_group_slot([] , []).	
get_hash_group_slot([(_ , _ , _ , [] , _ ,_,_) | T] ,L):- 
	get_hash_group_slot(T , L).
get_hash_group_slot([(_ , Semester , _ , [Tutorial|Tutorials] , _ ,_,E) | T] ,[Hash | L]):-
	Hash #= Semester  * 20 * 30  + Tutorial * 30 + (E mod 30),
	get_hash_group_slot([(_ , Semester , _ , Tutorials , _ ,_,E) | T] ,L).
		
get_hash_staff_slot([] , []).	
get_hash_staff_slot([(StaffID , _ , _ , _ , _ ,_,E) | T] , [Hash | L]):-
	Hash #= StaffID * 30 + (E mod 30),
	get_hash_staff_slot(T , L).
			
same_RoomType_compare(E , RoomType , B):- Z #= (E // 30) mod 4 , Z #= RoomType #<==> B.	

all_in_free_rooms([] , _).
all_in_free_rooms([E | T] ,  FreeRooms):- element(_,FreeRooms , E) , all_in_free_rooms(T , FreeRooms).