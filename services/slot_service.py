from datetime import datetime, timedelta


def generate_slots(
    working_start,
    working_end,
    slot_duration
):

    start = datetime.strptime(
        working_start,
        "%H:%M"
    )

    end = datetime.strptime(
        working_end,
        "%H:%M"
    )

    duration = timedelta(
        minutes=slot_duration
    )

    slots = []

    current = start

    while current + duration <= end:

        slot_start = current
        slot_end = current + duration

        slots.append({
            "start": slot_start.strftime("%H:%M"),
            "end": slot_end.strftime("%H:%M")
        })

        current += duration

    return slots