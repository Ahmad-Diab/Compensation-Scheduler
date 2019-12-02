var moment = require('moment');

module.exports =
{
    isSameWeek: (firstDate, secondDate) =>
    {
        moment.locale('en', {week: {dow: 6}});
        return moment(firstDate).isSame(secondDate, 'week');
    }
}