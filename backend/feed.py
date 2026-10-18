from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import hash_password

from app.models.user import User
from app.models.lead import Lead, LeadStatus, LeadPriority
from app.models.contact import Contact
from app.models.notes import Note
from app.models.task import Task, TaskStatus, TaskPriority


# ============================================================
# Helpers
# ============================================================

def now_utc():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def days_ago(days: int):
    return now_utc() - timedelta(days=days)


def days_ahead(days: int):
    return now_utc() + timedelta(days=days)


# ============================================================
# Seed Database
# ============================================================

def seed_database(db: Session):

    print("Starting database seed...")

    try:

        # ====================================================
        # User
        # ====================================================

        user = (
            db.query(User)
            .filter(User.email == "alex@timetoprogram.com")
            .first()
        )

        if not user:

            user = User(
                name="Alex Carter",
                email="alex@timetoprogram.com",
                password_hash=hash_password("Alex123!"),
                phone="+1 555 0100",
                role="owner",
                company="Time To Program",
                avatar="",
                created_at=days_ago(240),
            )

            db.add(user)
            db.flush()

            print("Created user")
            print("Login email: alex@timetoprogram.com")
            print("Login password: Alex123!")

        else:
            print("User already exists")

        owner_id = user.id

        # ====================================================
        # Leads
        # ====================================================

        leads_data = [
            ("Dribbble Design", "Acme Corp", "New", "High", "Website", 89345, 8),
            ("Google Pay", "Globex", "Qualified", "High", "Referral", 124000, 20),
            ("Amazon Shopping", "Initech", "Proposal", "Medium", "Cold Outreach", 32123, 35),
            ("Stripe", "Umbrella Co", "Won", "High", "Event", 76500, 60),
            ("Notion", "Soylent", "New", "Low", "Social", 12400, 4),
            ("Figma", "Hooli", "Qualified", "Medium", "Website", 54000, 14),
            ("Linear", "Pied Piper", "Proposal", "High", "Referral", 98000, 28),
            ("Slack", "Vehement", "Lost", "Low", "Cold Outreach", 21000, 95),
            ("Vercel", "Massive Dynamic", "Won", "High", "Referral", 143000, 110),
            ("Airtable", "Wayne Ent.", "Qualified", "High", "Event", 67000, 18),
            ("Datadog", "Stark Industries", "New", "Medium", "Website", 45000, 2),
            ("Snowflake", "Cyberdyne", "Proposal", "High", "Referral", 152000, 48),
            ("HubSpot", "Tyrell Corp", "Won", "Medium", "Event", 88000, 150),
            ("Asana", "Aperture Labs", "Qualified", "Low", "Social", 30000, 22),
            ("Zoom", "Oscorp", "New", "Medium", "Cold Outreach", 26000, 6),
            ("GitLab", "LexCorp", "Lost", "Low", "Website", 18000, 70),
        ]

        leads = []

        for (
            name,
            company,
            status,
            priority,
            source,
            value,
            age_days,
        ) in leads_data:

            existing = (
                db.query(Lead)
                .filter(
                    Lead.owner_id == owner_id,
                    Lead.name == name,
                    Lead.company == company,
                )
                .first()
            )

            if existing:
                leads.append(existing)
                continue

            email_name = (
                name.lower()
                .replace(" ", "")
                .replace("-", "")
            )

            company_name = (
                company.lower()
                .replace(" ", "")
                .replace(".", "")
            )

            email = f"{email_name}@{company_name}.com"

            phone = f"+1 555 0{len(leads) + 101}"

            notes = (
                "Closed — annual contract signed."
                if status == "Won"
                else "Active opportunity in the pipeline."
            )

            lead = Lead(
                owner_id=owner_id,
                name=name,
                email=email,
                phone=phone,
                company=company,
                status=LeadStatus(status),
                priority=LeadPriority(priority),
                source=source,
                value=value,
                notes=notes,
                tags=["saas"],
                sort_order=0,
                ai_summary="",
                ai_risk_score=None,
                created_at=days_ago(age_days),
                updated_at=days_ago(max(0, age_days // 4)),
            )

            db.add(lead)
            leads.append(lead)

        # Generate database IDs
        db.flush()

        print(f"Created {len(leads)} leads")

        # ====================================================
        # Lead ID Map
        #
        # IMPORTANT:
        # Never assume:
        # Amazon Shopping = ID 3
        #
        # PostgreSQL generates the real IDs.
        # ====================================================

        lead_map = {
            lead.name: lead._id
            for lead in leads
        }

        # ====================================================
        # Contacts
        # ====================================================

        contacts_data = [
            (
                "Olivia Bennett",
                "VP of Sales",
                "Acme Corp",
                "olivia@acmecorp.com",
                "+1 555 0101",
                ["decision-maker", "warm"],
                True,
                7,
            ),
            (
                "Noah Carter",
                "CTO",
                "Globex",
                "noah@globex.com",
                "+1 555 0102",
                ["technical", "champion"],
                True,
                14,
            ),
            (
                "Emma Walsh",
                "Procurement Manager",
                "Initech",
                "emma@initech.com",
                "+1 555 0103",
                ["finance"],
                False,
                21,
            ),
            (
                "Liam Foster",
                "Founder",
                "Umbrella Co",
                "liam@umbrellaco.com",
                "+1 555 0104",
                ["executive"],
                False,
                28,
            ),
            (
                "Ava Mitchell",
                "Head of Operations",
                "Hooli",
                "ava@hooli.com",
                "+1 555 0105",
                ["warm"],
                False,
                35,
            ),
            (
                "Ethan Brooks",
                "Product Lead",
                "Pied Piper",
                "ethan@piedpiper.com",
                "+1 555 0106",
                ["champion", "technical"],
                True,
                42,
            ),
            (
                "Sophia Reed",
                "Marketing Director",
                "Wayne Ent.",
                "sophia@wayneent.com",
                "+1 555 0107",
                ["influencer"],
                False,
                49,
            ),
            (
                "Mason Hayes",
                "CFO",
                "Cyberdyne",
                "mason@cyberdyne.com",
                "+1 555 0108",
                ["finance", "executive"],
                False,
                56,
            ),
            (
                "Isabella Diaz",
                "Head of Growth",
                "Stark Industries",
                "isabella@starkindustries.com",
                "+1 555 0109",
                ["vip", "warm"],
                False,
                63,
            ),
            (
                "Lucas Park",
                "Engineering Manager",
                "Tyrell Corp",
                "lucas@tyrellcorp.com",
                "+1 555 0110",
                ["technical"],
                False,
                70,
            ),
        ]

        contacts = []

        for (
            name,
            title,
            company,
            email,
            phone,
            tags,
            favorite,
            age_days,
        ) in contacts_data:

            existing = (
                db.query(Contact)
                .filter(
                    Contact.owner_id == owner_id,
                    Contact.name == name,
                    Contact.company == company,
                )
                .first()
            )

            if existing:
                contacts.append(existing)
                continue

            contact = Contact(
                owner_id=owner_id,
                name=name,
                title=title,
                company=company,
                email=email,
                phone=phone,
                tags=tags,
                favorite=favorite,
                created_at=days_ago(age_days),
                updated_at=days_ago(age_days),
            )

            db.add(contact)
            contacts.append(contact)

        db.flush()

        print(f"Created {len(contacts)} contacts")

        # ====================================================
        # Contact ID Map
        # ====================================================

        contact_map = {
            contact.name: contact._id
            for contact in contacts
        }

        # ====================================================
        # Notes
        # ====================================================

        notes_data = [
            (
                "Decision expected end of month. Loop in a solutions engineer for the technical review.",
                "Google Pay",
                True,
                3,
            ),
            (
                "Pricing pushback on the Pro tier — prepare an ROI one-pager before the next call.",
                "Amazon Shopping",
                False,
                6,
            ),
            (
                "Champion is leaving the company; identify a backup stakeholder ASAP.",
                "Linear",
                True,
                9,
            ),
            (
                "Security questionnaire + SOC 2 report requested. Sent to the trust center.",
                "Snowflake",
                False,
                12,
            ),
            (
                "Great discovery call — strong interest in the analytics module.",
                "Dribbble Design",
                False,
                1,
            ),
            (
                "Expansion likely next quarter — multi-year deal already signed.",
                "Vercel",
                False,
                18,
            ),
            (
                "Scheduling a technical deep-dive with the engineering team.",
                "Airtable",
                False,
                5,
            ),
            (
                "Early stage, budget unconfirmed. Re-engage in two weeks.",
                "Notion",
                False,
                2,
            ),
        ]

        notes = []

        for (
            content,
            lead_name,
            pinned,
            age_days,
        ) in notes_data:

            # Current Note model does not have lead_id.
            #
            # We therefore store the note without a lead
            # relationship for now.

            existing = (
                db.query(Note)
                .filter(
                    Note.content == content,
                )
                .first()
            )

            if existing:
                notes.append(existing)
                continue

            note = Note(
                content=content,
                contact_id=None,
                pinned=pinned,
                created_at=days_ago(age_days),
            )

            db.add(note)
            notes.append(note)

        db.flush()

        print(f"Created {len(notes)} notes")

        # ====================================================
        # Tasks
        # ====================================================

        tasks_data = [
            (
                "Send proposal follow-up to Initech",
                "High",
                "Pending",
                "Amazon Shopping",
                2,
            ),
            (
                "Schedule technical deep-dive with Wayne Ent.",
                "Medium",
                "In Progress",
                "Airtable",
                3,
            ),
            (
                "Quarterly check-in with Massive Dynamic",
                "Low",
                "Pending",
                "Vercel",
                7,
            ),
            (
                "Draft ROI one-pager for Initech",
                "High",
                "Completed",
                "Amazon Shopping",
                -4,
            ),
            (
                "Negotiate pricing with Cyberdyne",
                "High",
                "Pending",
                "Snowflake",
                0,
            ),
            (
                "Share case study with Globex",
                "Medium",
                "Pending",
                "Google Pay",
                1,
            ),
            (
                "Confirm contract redlines with Pied Piper",
                "High",
                "In Progress",
                "Linear",
                -1,
            ),
            (
                "Book discovery call with Oscorp",
                "Low",
                "Pending",
                "Zoom",
                5,
            ),
            (
                "Send security docs to Cyberdyne",
                "Medium",
                "Completed",
                "Snowflake",
                -8,
            ),
            (
                "Re-engage stalled deal at Soylent",
                "Low",
                "Pending",
                "Notion",
                14,
            ),
        ]

        tasks = []

        for (
            title,
            priority,
            status,
            lead_name,
            due_offset,
        ) in tasks_data:

            # Get actual generated lead ID
            lead_id = lead_map.get(lead_name)

            if lead_id is None:
                raise ValueError(
                    f"Lead '{lead_name}' was not found in lead_map"
                )

            existing = (
                db.query(Task)
                .filter(
                    Task.title == title,
                    Task.related_lead_id == lead_id,
                )
                .first()
            )

            if existing:
                tasks.append(existing)
                continue

            completed_at = (
                days_ago(1)
                if status == "Completed"
                else None
            )

            if due_offset < 0:
                due_date = days_ago(abs(due_offset))
            else:
                due_date = days_ahead(due_offset)

            task = Task(
                title=title,
                description="",
                due_date=due_date,
                completed_at=completed_at,
                status=TaskStatus(status),
                priority=TaskPriority(priority),
                related_lead_id=lead_id,
                related_contact_id=None,
                created_at=days_ago(2),
            )

            db.add(task)
            tasks.append(task)

        db.flush()

        print(f"Created {len(tasks)} tasks")

        # ====================================================
        # Commit
        # ====================================================

        db.commit()

        print("")
        print("============================================")
        print("Database seeding completed successfully!")
        print("============================================")
        print("")
        print("Seed user:")
        print("Email    : alex@timetoprogram.com")
        print("Password : Alex123!")
        print("")
        print(f"Owner ID : {owner_id}")
        print(f"Leads    : {len(leads)}")
        print(f"Contacts : {len(contacts)}")
        print(f"Notes    : {len(notes)}")
        print(f"Tasks    : {len(tasks)}")
        print("")

    except Exception:
        db.rollback()
        raise


# ============================================================
# Run
# ============================================================

if __name__ == "__main__":

    db = SessionLocal()

    try:

        seed_database(db)

    except Exception as e:

        print(f"Seed failed: {e}")
        raise

    finally:

        db.close()