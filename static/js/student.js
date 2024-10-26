document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('book-slot').addEventListener('click', function() {
        const slot_time = document.getElementById('slot-time').value;
        const course_id = document.getElementById('course-id').value;
        
        fetch('/student/book_slot', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                slot_time: slot_time,
                course_id: course_id
            })
        }).then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Slot booked successfully');
            }
        });
    });
});
