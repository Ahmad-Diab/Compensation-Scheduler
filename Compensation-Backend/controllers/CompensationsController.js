var config = require('../config/DBConnection'); 
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
    }
}