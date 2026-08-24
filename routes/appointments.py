from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
    session
)

from sqlalchemy.exc import IntegrityError

from extensions import db

from models.appointment import Appointment
from models.doctor import Doctor
from models.doctor_leave import DoctorLeave
from models.symptom import Symptom
from models.ai_summary import AISummary
from models.post_visit import PostVisitRecord

from services.ai_service import (
    generate_previsit_summary,
    generate_postvisit_summary
)


appointments = Blueprint(
    "appointments",
    __name__,
    url_prefix="/appointments"
)


# ============================================================
# PATIENT - BOOK APPOINTMENT PAGE
# ============================================================

@appointments.route("/book-page")
def book_page():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("user_role") != "patient":
        return "Access Denied", 403

    doctors = Doctor.query.all()

    return render_template(
        "patient/book.html",
        doctors=doctors
    )


# ============================================================
# GET AVAILABLE SLOTS
# ============================================================

@appointments.route("/available-slots", methods=["GET"])
@appointments.route("/slots", methods=["GET"])
def available_slots():

    if "user_id" not in session:
        return jsonify({
            "error": "Please login first"
        }), 401

    if session.get("user_role") != "patient":
        return jsonify({
            "error": "Access Denied"
        }), 403

    doctor_id = (
        request.args.get("doctor_id")
        or request.args.get("doctor")
    )

    appointment_date = (
        request.args.get("date")
        or request.args.get("appointment_date")
    )

    if not doctor_id or not appointment_date:
        return jsonify({
            "error": "Doctor and date are required"
        }), 400

    doctor = Doctor.query.get(doctor_id)

    if not doctor:
        return jsonify({
            "error": "Doctor not found"
        }), 404

    # --------------------------------------------------------
    # Check whether doctor is on leave
    # --------------------------------------------------------

    leave = DoctorLeave.query.filter_by(
        doctor_id=doctor.id,
        leave_date=appointment_date
    ).first()

    if leave:

        print(
            "Doctor is on leave:",
            doctor.id,
            appointment_date
        )

        return jsonify({
            "available": False,
            "slots": [],
            "message": "Doctor is on leave on this date."
        })

    from datetime import datetime, timedelta

    # --------------------------------------------------------
    # Doctor working hours
    # --------------------------------------------------------

    try:

        start_hour, start_minute = map(
            int,
            doctor.working_start.split(":")
        )

        end_hour, end_minute = map(
            int,
            doctor.working_end.split(":")
        )

        slot_duration = int(
            doctor.slot_duration
        )

    except Exception as e:

        print(
            "WORKING HOURS ERROR:",
            e
        )

        return jsonify({
            "error":
                "Invalid doctor working hours"
        }), 500

    start_time = datetime(
        2000,
        1,
        1,
        start_hour,
        start_minute
    )

    end_time = datetime(
        2000,
        1,
        1,
        end_hour,
        end_minute
    )

    # --------------------------------------------------------
    # Generate all slots
    # --------------------------------------------------------

    all_slots = []

    current_time = start_time

    while current_time + timedelta(
        minutes=slot_duration
    ) <= end_time:

        slot_end = (
            current_time +
            timedelta(minutes=slot_duration)
        )

        all_slots.append({
            "start":
                current_time.strftime("%H:%M"),

            "end":
                slot_end.strftime("%H:%M")
        })

        current_time = slot_end

    # --------------------------------------------------------
    # Find booked appointments
    #
    # Cancelled appointments do NOT block a slot.
    # --------------------------------------------------------

    booked = Appointment.query.filter(
        Appointment.doctor_id == doctor.id,
        Appointment.appointment_date == appointment_date,
        Appointment.status != "cancelled"
    ).all()

    booked_slots = set()

    for appointment in booked:

        start = appointment.start_time
        end = appointment.end_time

        if hasattr(start, "strftime"):
            start = start.strftime("%H:%M")
        else:
            start = str(start)[:5]

        if hasattr(end, "strftime"):
            end = end.strftime("%H:%M")
        else:
            end = str(end)[:5]

        booked_slots.add(
            (start, end)
        )

    # --------------------------------------------------------
    # Remove booked slots
    # --------------------------------------------------------

    available_slots = []

    for slot in all_slots:

        if (
            slot["start"],
            slot["end"]
        ) not in booked_slots:

            available_slots.append(slot)

    print("Doctor:", doctor.id)
    print("Date:", appointment_date)
    print("All slots:", all_slots)
    print("Booked slots:", booked_slots)
    print("Available slots:", available_slots)

    return jsonify({
        "available": True,
        "slots": available_slots
    })


# ============================================================
# PATIENT - BOOK APPOINTMENT
# ============================================================

@appointments.route("/book", methods=["POST"])
def book_appointment():

    if "user_id" not in session:
        return jsonify({
            "success": False,
            "error": "Please login first"
        }), 401

    if session.get("user_role") != "patient":
        return jsonify({
            "success": False,
            "error": "Access Denied"
        }), 403

    try:

        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "error": "Invalid request"
            }), 400

        doctor_id = data.get("doctor_id")
        appointment_date = data.get("appointment_date")
        start_time = data.get("start_time")
        end_time = data.get("end_time")
        symptoms_text = data.get("symptoms", "").strip()

        # ---------------------------------------------
        # VALIDATION
        # ---------------------------------------------

        if not doctor_id:
            return jsonify({
                "success": False,
                "error": "Please select a doctor."
            }), 400

        if not appointment_date:
            return jsonify({
                "success": False,
                "error": "Please select an appointment date."
            }), 400

        if not start_time or not end_time:
            return jsonify({
                "success": False,
                "error": "Please select an available time slot."
            }), 400

        if not symptoms_text:
            return jsonify({
                "success": False,
                "error": "Please enter your symptoms."
            }), 400

        # ---------------------------------------------
        # FIND DOCTOR
        # ---------------------------------------------

        doctor = Doctor.query.get(int(doctor_id))

        if not doctor:
            return jsonify({
                "success": False,
                "error": "Doctor not found."
            }), 404

        # ---------------------------------------------
        # CHECK LEAVE
        # ---------------------------------------------

        leave = DoctorLeave.query.filter_by(
            doctor_id=doctor.id,
            leave_date=appointment_date
        ).first()

        if leave:

            print(
                "BOOKING REJECTED - DOCTOR ON LEAVE",
                doctor.id,
                appointment_date
            )

            return jsonify({
                "success": False,
                "status": "rejected",
                "message":
                    "Booking rejected. "
                    "The doctor is on leave on this date."
            }), 409

        # ---------------------------------------------
        # CHECK SLOT
        # ---------------------------------------------

        existing_appointment = Appointment.query.filter(
            Appointment.doctor_id == doctor.id,
            Appointment.appointment_date == appointment_date,
            Appointment.start_time == start_time,
            Appointment.end_time == end_time,
            Appointment.status != "cancelled"
        ).first()

        if existing_appointment:

            return jsonify({
                "success": False,
                "status": "unavailable",
                "message":
                    "This appointment slot has already been booked."
            }), 409

        # ---------------------------------------------
        # CREATE APPOINTMENT
        # ---------------------------------------------

        appointment = Appointment(
            patient_id=session["user_id"],
            doctor_id=doctor.id,
            appointment_date=appointment_date,
            start_time=start_time,
            end_time=end_time,
            symptoms=symptoms_text,
            status="confirmed"
        )

        db.session.add(appointment)

        # Get ID without committing yet
        db.session.flush()

        # ---------------------------------------------
        # SAVE SYMPTOMS
        # ---------------------------------------------

        symptom = Symptom(
            appointment_id=appointment.id,
            symptoms_text=symptoms_text
        )

        db.session.add(symptom)

        # ---------------------------------------------
        # AI SUMMARY
        # ---------------------------------------------

        try:

            ai_result = generate_previsit_summary(
                symptoms_text
            )

            ai_summary = AISummary(
                appointment_id=appointment.id,

                chief_complaint=ai_result.get(
                    "chief_complaint",
                    "Not specified"
                ),

                key_symptoms=", ".join(
                    ai_result.get(
                        "key_symptoms",
                        []
                    )
                ),

                duration=ai_result.get(
                    "duration",
                    "Not specified"
                ),

                urgency=ai_result.get(
                    "urgency",
                    "Routine"
                ),

                suggested_questions="\n".join(
                    ai_result.get(
                        "suggested_questions",
                        []
                    )
                )
            )

            db.session.add(ai_summary)

        except Exception as ai_error:

            print(
                "AI SUMMARY ERROR:",
                ai_error
            )

            # Continue booking even if AI fails

        # ---------------------------------------------
        # COMMIT
        # ---------------------------------------------

        db.session.commit()

        print(
            "APPOINTMENT BOOKED SUCCESSFULLY:",
            appointment.id
        )

        return jsonify({
            "success": True,
            "status": "confirmed",
            "message":
                "Booking confirmed successfully.",
            "appointment_id":
                appointment.id
        }), 201

    except IntegrityError as e:

        db.session.rollback()

        print(
            "INTEGRITY ERROR:",
            e
        )

        return jsonify({
            "success": False,
            "status": "unavailable",
            "message":
                "This appointment slot has already been booked."
        }), 409

    except Exception as e:

        db.session.rollback()

        print(
            "APPOINTMENT BOOKING ERROR:",
            e
        )

        return jsonify({
            "success": False,
            "error":
                f"Unable to book appointment: {str(e)}"
        }), 500


# ============================================================
# PATIENT - MY APPOINTMENTS
# ============================================================

@appointments.route("/my-appointments")
def my_appointments():

    if "user_id" not in session:
        return redirect(
            url_for("auth.login")
        )

    if session.get("user_role") != "patient":
        return "Access Denied", 403

    appointments_list = (
        Appointment.query
        .filter_by(
            patient_id=session["user_id"]
        )
        .order_by(
            Appointment.appointment_date,
            Appointment.start_time
        )
        .all()
    )

    return render_template(
        "patient/appointments.html",
        appointments=appointments_list
    )


# ============================================================
# DOCTOR - MY APPOINTMENTS
# ============================================================

@appointments.route("/doctor")
def doctor_appointments():

    if "user_id" not in session:
        return redirect(
            url_for("auth.login")
        )

    if session.get("user_role") != "doctor":
        return "Access Denied", 403

    # --------------------------------------------------------
    # Find doctor profile
    # --------------------------------------------------------

    doctor = Doctor.query.filter_by(
        user_id=session["user_id"]
    ).first()

    if not doctor:
        return "Doctor profile not found", 404

    # --------------------------------------------------------
    # Get doctor's appointments
    # --------------------------------------------------------

    appointments_list = (
        Appointment.query
        .filter_by(
            doctor_id=doctor.id
        )
        .order_by(
            Appointment.appointment_date,
            Appointment.start_time
        )
        .all()
    )

    # --------------------------------------------------------
    # Get symptoms
    # --------------------------------------------------------

    appointment_symptoms = {}

    for appointment in appointments_list:

        symptom = Symptom.query.filter_by(
            appointment_id=appointment.id
        ).first()

        appointment_symptoms[
            appointment.id
        ] = symptom

    # --------------------------------------------------------
    # Get AI summaries
    # --------------------------------------------------------

    appointment_ai_summaries = {}

    for appointment in appointments_list:

        ai_summary = AISummary.query.filter_by(
            appointment_id=appointment.id
        ).first()

        appointment_ai_summaries[
            appointment.id
        ] = ai_summary

    return render_template(
        "doctor/appointments.html",

        appointments=appointments_list,

        appointment_symptoms=
            appointment_symptoms,

        appointment_ai_summaries=
            appointment_ai_summaries
    )


# ============================================================
# DOCTOR - REGENERATE AI SUMMARY
# ============================================================

@appointments.route(
    "/<int:appointment_id>/regenerate-summary",
    methods=["POST"]
)
def regenerate_summary(
    appointment_id
):

    if "user_id" not in session:
        return jsonify({
            "error": "Please login first"
        }), 401

    if session.get("user_role") != "doctor":
        return jsonify({
            "error": "Access Denied"
        }), 403

    # --------------------------------------------------------
    # Find doctor
    # --------------------------------------------------------

    doctor = Doctor.query.filter_by(
        user_id=session["user_id"]
    ).first()

    if not doctor:
        return jsonify({
            "error":
                "Doctor profile not found"
        }), 404

    # --------------------------------------------------------
    # Find appointment
    # --------------------------------------------------------

    appointment = Appointment.query.get(
        appointment_id
    )

    if not appointment:
        return jsonify({
            "error": "Appointment not found"
        }), 404

    # --------------------------------------------------------
    # Verify appointment belongs to doctor
    # --------------------------------------------------------

    if appointment.doctor_id != doctor.id:

        return jsonify({
            "error": "Access Denied"
        }), 403

    # --------------------------------------------------------
    # Find symptoms
    # --------------------------------------------------------

    symptom = Symptom.query.filter_by(
        appointment_id=appointment.id
    ).first()

    if not symptom:

        return jsonify({
            "error":
                "No symptoms found for this appointment"
        }), 404

    try:

        print(
            "Regenerating AI summary for appointment:",
            appointment.id
        )

        # ----------------------------------------------------
        # Generate new AI summary
        # ----------------------------------------------------

        ai_result = generate_previsit_summary(
            symptom.symptoms_text
        )

        # ----------------------------------------------------
        # Find existing summary
        # ----------------------------------------------------

        ai_summary = AISummary.query.filter_by(
            appointment_id=appointment.id
        ).first()

        # ----------------------------------------------------
        # Create if it doesn't exist
        # ----------------------------------------------------

        if not ai_summary:

            ai_summary = AISummary(
                appointment_id=appointment.id
            )

            db.session.add(ai_summary)

        # ----------------------------------------------------
        # Update summary
        # ----------------------------------------------------

        ai_summary.chief_complaint = (
            ai_result.get(
                "chief_complaint",
                "Not specified"
            )
        )

        ai_summary.key_symptoms = ", ".join(
            ai_result.get(
                "key_symptoms",
                []
            )
        )

        ai_summary.duration = (
            ai_result.get(
                "duration",
                "Not specified"
            )
        )

        ai_summary.urgency = (
            ai_result.get(
                "urgency",
                "Routine"
            )
        )

        ai_summary.suggested_questions = (
            "\n".join(
                ai_result.get(
                    "suggested_questions",
                    []
                )
            )
        )

        db.session.commit()

        return jsonify({
            "success": True,
            "message":
                "AI summary regenerated successfully"
        })

    except Exception as e:

        db.session.rollback()

        print(
            "REGENERATE AI SUMMARY ERROR:",
            e
        )

        return jsonify({
            "error":
                "Unable to regenerate AI summary"
        }), 500


# ============================================================
# DOCTOR - UPDATE APPOINTMENT STATUS
# ============================================================

@appointments.route(
    "/<int:appointment_id>/status",
    methods=["POST"]
)
def update_appointment_status(
    appointment_id
):

    if "user_id" not in session:
        return jsonify({
            "error": "Please login first"
        }), 401

    if session.get("user_role") != "doctor":
        return jsonify({
            "error": "Access Denied"
        }), 403

    # --------------------------------------------------------
    # Find logged-in doctor
    # --------------------------------------------------------

    doctor = Doctor.query.filter_by(
        user_id=session["user_id"]
    ).first()

    if not doctor:

        return jsonify({
            "error":
                "Doctor profile not found"
        }), 404

    # --------------------------------------------------------
    # Find appointment
    # --------------------------------------------------------

    appointment = Appointment.query.get(
        appointment_id
    )

    if not appointment:

        return jsonify({
            "error": "Appointment not found"
        }), 404

    # --------------------------------------------------------
    # Verify ownership
    # --------------------------------------------------------

    if appointment.doctor_id != doctor.id:

        return jsonify({
            "error": "Access Denied"
        }), 403

    # --------------------------------------------------------
    # Get new status
    # --------------------------------------------------------

    data = request.get_json()

    if not data:

        return jsonify({
            "error": "Invalid request"
        }), 400

    new_status = data.get(
        "status"
    )

    allowed_statuses = [
        "booked",
        "confirmed",
        "completed",
        "cancelled"
    ]

    if new_status not in allowed_statuses:

        return jsonify({
            "error":
                "Invalid appointment status"
        }), 400

    # --------------------------------------------------------
    # Update status
    # --------------------------------------------------------

    appointment.status = new_status

    try:

        db.session.commit()

        return jsonify({
            "success": True,

            "message":
                f"Appointment {new_status} successfully",

            "status":
                new_status
        })

    except Exception as e:

        db.session.rollback()

        print(
            "STATUS UPDATE ERROR:",
            e
        )

        return jsonify({
            "error":
                "Unable to update appointment status"
        }), 500

# ============================================================
# DOCTOR - SUBMIT POST-VISIT NOTES
# ============================================================

@appointments.route(
    "/<int:appointment_id>/post-visit",
    methods=["POST"]
)
def submit_post_visit(
    appointment_id
):

    if "user_id" not in session:
        return jsonify({
            "success": False,
            "error": "Please login first"
        }), 401

    if session.get("user_role") != "doctor":
        return jsonify({
            "success": False,
            "error": "Access Denied"
        }), 403

    # --------------------------------------------------------
    # Find logged-in doctor
    # --------------------------------------------------------

    doctor = Doctor.query.filter_by(
        user_id=session["user_id"]
    ).first()

    if not doctor:
        return jsonify({
            "success": False,
            "error": "Doctor profile not found"
        }), 404

    # --------------------------------------------------------
    # Find appointment
    # --------------------------------------------------------

    appointment = Appointment.query.get(
        appointment_id
    )

    if not appointment:
        return jsonify({
            "success": False,
            "error": "Appointment not found"
        }), 404

    # --------------------------------------------------------
    # Verify appointment belongs to doctor
    # --------------------------------------------------------

    if appointment.doctor_id != doctor.id:
        return jsonify({
            "success": False,
            "error": "Access Denied"
        }), 403

    # --------------------------------------------------------
    # Get form/JSON data
    # --------------------------------------------------------

    if request.is_json:

        data = request.get_json()

        diagnosis = (
            data.get("diagnosis", "")
            .strip()
        )

        post_visit_notes = (
            data.get("post_visit_notes", "")
            .strip()
        )

        prescription = (
            data.get("prescription", "")
            .strip()
        )

        follow_up_instructions = (
            data.get(
                "follow_up_instructions",
                ""
            ).strip()
        )

    else:

        diagnosis = (
            request.form.get(
                "diagnosis",
                ""
            ).strip()
        )

        post_visit_notes = (
            request.form.get(
                "post_visit_notes",
                ""
            ).strip()
        )

        prescription = (
            request.form.get(
                "prescription",
                ""
            ).strip()
        )

        follow_up_instructions = (
            request.form.get(
                "follow_up_instructions",
                ""
            ).strip()
        )

    # --------------------------------------------------------
    # Validate doctor's notes
    # --------------------------------------------------------

    if not post_visit_notes:

        return jsonify({
            "success": False,
            "error":
                "Post-visit notes are required."
        }), 400

    # --------------------------------------------------------
    # Check whether a post-visit record already exists
    # --------------------------------------------------------

    post_visit = PostVisitRecord.query.filter_by(
        appointment_id=appointment.id
    ).first()

    # --------------------------------------------------------
    # Generate patient-friendly AI summary
    # --------------------------------------------------------

    ai_summary = None

    try:

        print(
            "Generating post-visit summary for:",
            appointment.id
        )

        ai_summary = generate_postvisit_summary(
            diagnosis=diagnosis,
            post_visit_notes=post_visit_notes,
            prescription=prescription,
            follow_up_instructions=
                follow_up_instructions
        )

    except Exception as ai_error:

        print(
            "POST-VISIT AI SUMMARY ERROR:",
            ai_error
        )

        # The doctor's medical record can still
        # be saved even if the AI service fails.

        ai_summary = (
            "Patient-friendly summary could not "
            "be generated automatically. "
            "Please refer to the doctor's notes "
            "and prescription."
        )

    # --------------------------------------------------------
    # Create or update post-visit record
    # --------------------------------------------------------

    if post_visit:

        post_visit.diagnosis = diagnosis

        post_visit.post_visit_notes = (
            post_visit_notes
        )

        post_visit.prescription = (
            prescription
        )

        post_visit.follow_up_instructions = (
            follow_up_instructions
        )

        post_visit.ai_summary = ai_summary

    else:

        post_visit = PostVisitRecord(

            appointment_id=appointment.id,

            doctor_id=doctor.id,

            patient_id=appointment.patient_id,

            diagnosis=diagnosis,

            post_visit_notes=post_visit_notes,

            prescription=prescription,

            follow_up_instructions=
                follow_up_instructions,

            ai_summary=ai_summary
        )

        db.session.add(post_visit)

    # --------------------------------------------------------
    # Mark appointment as completed
    # --------------------------------------------------------

    appointment.status = "completed"

    # --------------------------------------------------------
    # Save everything
    # --------------------------------------------------------

    try:

        db.session.commit()

        print(
            "POST-VISIT RECORD SAVED:",
            appointment.id
        )

        return jsonify({

            "success": True,

            "message":
                "Post-visit notes submitted successfully.",

            "appointment_id":
                appointment.id,

            "status":
                appointment.status,

            "ai_summary":
                ai_summary
        })

    except Exception as e:

        db.session.rollback()

        print(
            "POST-VISIT SAVE ERROR:",
            e
        )

        return jsonify({
            "success": False,
            "error":
                "Unable to save post-visit information."
        }), 500