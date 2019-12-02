var moment = require('moment');

module.exports =
{
    isSameWeek: (firstDate, secondDate) =>
    {
        moment.locale('en', {week: {dow: 6}});
        return moment(firstDate).isSame(secondDate, 'week');
    },

    getWeekDates: (date) =>
    {
        moment.locale('en', {week: {dow: 6}});
        var allDatesInWeek = [];
        for(var i = 0; i < 7; i++)
        {
            if(this.isSameWeek(firstDate, moment(date).day(i)))
                allDatesInWeek.push(moment(date).day(i));
        }
        return allDatesInWeek;
    },

    fromSlotToDay: (slot) =>
    {
        if(slot < 6) return 'Saturday';
        if(slot > 5 && slot < 11) return 'Sunday';
        if(slot > 10 && slot < 16) return 'Monday';
        if(slot > 15 && slot < 21) return 'Tuesday';
        if(slot > 20 && slot < 26) return 'Wednesday';
        return 'Thursday';
    },

    getDayIdx: (day) => 
    {
        if(day == 'Saturday') return 1;
        if(day == 'Sunday') return 2;
        if(day == 'Monday') return 3;
        if(day == 'Tuesday') return 4;
        if(day == 'Wednesday') return 5;
        return 6;
    }
}