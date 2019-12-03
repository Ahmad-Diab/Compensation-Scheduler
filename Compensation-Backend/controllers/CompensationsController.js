var mysql  = require('mysql')
var moment    = require('moment')
var constants = require('../utils/Constants');
var helpers = require('../utils/Helpers');
const util = require('util');



module.exports =
{
    getSlotsToBeCompensated: async (req, res, next) =>
    {
        var staffMemberID = req.query.staffMemberID;

        // Connect to DB
        var con = mysql.createConnection({
            host: "localhost",
            user: "root",
            password: "password",
            database: "GUCDataBase"
          });
          
        con.connect(function(err) {
            if (err) throw err;
            console.log("Connected To Database!");
        });

        // node native promisify
        const query = util.promisify(con.query).bind(con);

        var findSlotsMatchingWithHolidays = "SELECT cm.id AS meeting_id, c.date AS date, cm.day AS day, cm.slot AS slot, cm.course_id AS course_id, cm.lecture_group_id AS lecture_group, cm.tutorial_group_id AS tutorial_group, cm.start_date AS start_date, cm.end_date AS end_date, cm.mid_term_start_date AS mid_term_start_date, cm.mid_term_end_date AS mid_term_end_date FROM Course_Meetings cm, Calendar_Holidays c WHERE cm.day = c.day AND c.event_name = '" 
                                            + constants.CALENDAR_EVENTS.HOLIDAY + "' AND cm.staff_member_id = " + staffMemberID;

        var needCompensation = [];
        var daysMatchingHolidays = await query(findSlotsMatchingWithHolidays);            
        for(var i = 0; i < daysMatchingHolidays.length; i++)
        {
            var isCompensated = 'SELECT * FROM Compensations WHERE meeting_id = ' + daysMatchingHolidays[i].meeting_id;
            var compensations = await query(isCompensated);
            for(var j = 0; j < compensations.length; j++)
            {
                if(!helpers.isSameWeek(compensations[j], daysMatchingHolidays[i].date) && 
                    moment(daysMatchingHolidays[i].date).isBefore(daysMatchingHolidays[i].end_date) && moment(daysMatchingHolidays[i].date).isAfter(daysMatchingHolidays[i].start_date)
                    && (moment(daysMatchingHolidays[i].date).isBefore(daysMatchingHolidays[i].mid_term_start_date) || moment(daysMatchingHolidays[i].date).isAfter(daysMatchingHolidays[i].mid_term_end_date)))
                {
                    needCompensation.push({meeting_id: daysMatchingHolidays[i].meeting_id, date: daysMatchingHolidays[i].date, day: daysMatchingHolidays[i].day, slot: daysMatchingHolidays[i].slot,
                                            course_id: daysMatchingHolidays[i].course_id, lecture_group_id: lecture_group, tutorial_group_id: tutorial_group});
                }
            }

            if(compensations.length == 0)
            {
                needCompensation.push({meeting_id: daysMatchingHolidays[i].meeting_id, date: daysMatchingHolidays[i].date, day: daysMatchingHolidays[i].day, slot: daysMatchingHolidays[i].slot,
                                        course_id: daysMatchingHolidays[i].course_id, lecture_group_id: daysMatchingHolidays[i].lecture_group, tutorial_group_id: daysMatchingHolidays[i].tutorial_group});
            }
        }

        con.end();

        return res.status(200).json({compensation_required: needCompensation});
    },

    compensateSlots: async (req, res, next) => 
    {
        var staffMemberID           = req.body.staffMemberID;
        // Meetings Should be of the same day
        var meetingsToBeCompensated = req.body.meetingsIDs;
        // Prefered Slots should be of the same week
        var preferredSlots          = req.body.preferredSlots;
        // UnPreferred Slots should be of the same week
        var unPreferredSlots        = req.body.unPreferredSlots;
        // Holiday Date
        var holidayDate             = req.body.holidayDate;
        // Holiday Day              
        var holidayDay              = req.body.holidayDay;

        var daysInWeek = helpers.getWeekDates(holidayDate);

        // Connect to DB
        var con = mysql.createConnection({
            host: "localhost",
            user: "root",
            password: "password",
            database: "GUCDataBase"
          });
          
        con.connect(function(err) {
            if (err) throw err;
            console.log("Connected To Database!");
        });

        // node native promisify
        const query = util.promisify(con.query).bind(con);

        var availableDates = [];
        for(var i = 0; i < daysInWeek.length; i++)
        {
            var findDayIsAHoliday = "SELECT * FROM Calendar_Holidays WHERE date = '" + daysInWeek[i] + "' AND event_name = '" 
                                + constants.CALENDAR_EVENTS.HOLIDAY + "'";
            var dayIsHoliday = await query(findDayIsAHoliday);
            if(dayIsHoliday.length == 0)
                availableDates.push(daysInWeek[i]);
        }

        // Slots is meetings_ids, type
        // solve_all_slots(Slots , Days_Off, FreeSlots, FreeLargeHalls, FreeSmallHalls, FreeRooms, FreeLabs, Preferable , NonPreferable).

        var meetingsWithRoomType = [];
        // GET STUDENTS DAYS OFF
        var studentsByMeetingDaysOff = [];
        // GET STUDENTS FREE SLOTS
        var studentsByMeetingFreeSlots = [];
        for(var i = 0; i < meetingsToBeCompensated.length; i++)
        {
            var meetingDaysOff = [];

            var getMeetingQuery = "SELECT * FROM Course_Meetings WHERE id = " + meetingsToBeCompensated[i];
            var courseMeeting = await query(getMeetingQuery);

            // Get Meeting along With Type
            var getRoomTypeQuery = "SELECT * FROM Rooms WHERE id = " + courseMeeting.room_id;
            var roomType = await query(getRoomTypeQuery);
            meetingsWithRoomType.push([meetingsToBeCompensated[i], roomType[0].room_type]);

            // GET DAYS OFF HERE
            var daysOffQuery = null;
            if(courseMeeting.tutorial_group_id == null)
                daysOffQuery = "SELECT DISTINCT day FROM Tutorial_Groups_Holidays WHERE lecture_group_id = " + courseMeeting.lecture_group_id;
            else
                daysOffQuery = "SELECT DISTINCT day FROM Tutorial_Groups_Holidays WHERE tutorial_group_id = " + courseMeeting.tutorial_group_id;

            var daysOff = await query(daysOffQuery);
            for(var j = 0; j < daysOff.length; j++)
                if(daysOff[i].day != holidayDay)
                    meetingDaysOff.push(helpers.getDayIdx(daysOff[j].day));

            // ADD FREE SLOTS HERE
            var occupiedSlotsQuery = null;
            if(courseMeeting.tutorial_group_id == null)
                occupiedSlotsQuery = "SELECT * FROM Course_Meetings WHERE lecture_group_id = " + courseMeeting.lecture_group_id;
            else
                occupiedSlotsQuery = "SELECT * FROM Course_Meetings WHERE tutorial_group_id = " + courseMeeting.tutorial_group_id;

            var occupiedSlots = await query(occupiedSlotsQuery);
            var notEmptySlots = new Set();
            for(var j = 0; j < occupiedSlots.length; j++)
                if(occupiedSlots[j].day != holidayDay)
                    notEmptySlots.add(helpers.getNumberOfPreviousSlots(occupiedSlots[j].day) + occupiedSlots[j].slot);

            var freeSlots = [];
            for(var j = 1; j <= 30; j++)
                if(!notEmptySlots.has(j) && helpers.fromSlotToDay(j) != holidayDay)
                    freeSlots.push(j);
            
            studentsByMeetingDaysOff.push(meetingDaysOff);
            studentsByMeetingFreeSlots.push(freeSlots)
        }

        // Find Empty Rooms at Each Slot
        var emptyRooms = [];
        var emptyLabs = [];
        var emptyLargeHalls = [];
        var emptySmallHalls = [];
        for(var i = 1; i <= 6; i++)
        {
            var day = helpers.fromIdxToDay(i);
            for(var j = 1; j <= 5; j++)
            {
                var findEmptyRoomsQuery = "SELECT * FROM Rooms WHERE type = 'Room' AND id NOT IN (SELECT room_id FROM Course_Meetings WHERE day = '"
                                         + day + "'AND slot = " + j + " )";
                var findEmptyLargeHallsQuery = "SELECT * FROM Rooms WHERE type = 'LargeHall' AND id NOT IN (SELECT room_id FROM Course_Meetings WHERE day = '"
                                         + day + "'AND slot = " + j + " )";
                var findEmptySmallHallsQuery = "SELECT * FROM Rooms WHERE type = 'SmallHall' AND id NOT IN (SELECT room_id FROM Course_Meetings WHERE day = '"
                                         + day + "'AND slot = " + j + " )";
                var findEmptyLabsQuery = "SELECT * FROM Rooms WHERE type = 'Lab' AND id NOT IN (SELECT room_id FROM Course_Meetings WHERE day = '"
                                         + day + "'AND slot = " + j + " )";
                
                var findEmptyRooms = await query(findEmptyRoomsQuery);
                var findEmptyLargeHalls = await query(findEmptyLargeHallsQuery);
                var findEmptySmallHalls = await query(findEmptySmallHallsQuery);
                var findEmptyLabs = await query(findEmptyLabsQuery);

                for(var c = 0; c < findEmptyRooms.length; c++)
                    emptyRooms.push(findEmptyRooms[c].id);
                
                for(var c = 0; c < findEmptyLabs.length; c++)
                    emptyLabs.push(findEmptyLabs[c].id);

                for(var c = 0; c < findEmptyLargeHalls.length; c++)
                    emptyLargeHalls.push(findEmptyLargeHalls[c].id);
                
                for(var c = 0; c < findEmptySmallHalls.length; c++)
                    emptySmallHalls.push(findEmptySmallHalls[c].id);
            }
        }


        // CALL PROLOG PREDICATE HERE
    }
}