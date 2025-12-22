# Business Requirements Document (BRD) - Agas Ashram V2

## 1. Project Overview
The Agas Ashram V2 application is designed to manage visitor interactions with the Ashram. It provides a centralized platform for users to create profiles, manage family member details, register for various events/programs, and communicate with the Ashram administration.

## 2. Business Objectives
- **Centralized Visitor Database**: Maintain a comprehensive and accurate record of all visitors and their family members.
- **Streamlined Event Registration**: Simplify the process for visitors to sign up for events and manage their stay.
- **Enhanced Communication**: Provide a direct channel for visitors to reach out for support or inquiries.
- **Resource Management**: Efficiently track room availability and visitor counts for better logistics planning.

## 3. Key Stakeholders
- **Ashram Administration**: Manages event schedules, room allocations, and reviews visitor data.
- **General Visitors**: Individuals and families visiting the Ashram for events or stays.
- **Support Staff**: Handles inquiries submitted through the contact platform.

## 4. Functional Requirements

### 4.1 User Authentication & Account Management
- **FR1: OTP-Based Signup/Login**: Users shall register and log in using a one-time password (OTP) sent to their verified email address or mobile number.
- **FR2: Persistent Login Sessions**: The system shall maintain user sessions to allow access to personal data and registration history without frequent logins.

### 4.2 Profile Management
- **FR3: Comprehensive Personal Profile**: Users shall maintain a profile including name, contact details, date of birth, age, gender, address, and ID proof.
- **FR4: Family Member Management**: Users shall be able to add and manage details for family members or regular co-visitors, including their personal information and ID documents.
- **FR5: Mandatory ID Documentation**: The system shall allow users to upload photos and ID proofs for themselves and their family members for security verification.

### 4.3 Event & Program Registration
- **FR6: Event Program Listing**: Users shall be able to view a list of upcoming events/programs hosted by the Ashram.
- **FR7: Group Registration**: Users shall be able to register for an event for themselves and select which previously saved family members will be accompanying them.
- **FR8: Accommodation Booking**: During registration, users shall specify their stay duration (Check-in/Check-out dates) and the number of rooms required.
- **FR9: Meal Preferences**: Users shall be able to specify meal requirements (Breakfast, Lunch, Dinner) for themselves and their group during the stay.
- **FR10: Room Type Selection**: Users shall select preferred room types from the available inventory (linked to Room Master).

### 4.4 My Registrations & History
- **FR11: Registration Dashboard**: Users shall have a dedicated view to see all their current and past event registrations.
- **FR12: Registration Cancellation**: Users shall be able to cancel an existing registration, providing a reason for cancellation.
- **FR13: Registration Details View**: Users shall be able to view detailed summaries of any specific registration, including guest lists and meal plans.

### 4.5 Support & Communication
- **FR14: Public Contact Form**: A "Contact Us" feature shall be available for both guest and registered users to send inquiries to the administration.
- **FR15: Automated Email Notifications**: The system shall send automated confirmation emails for profile creation, successful event registration, and registration cancellations.

## 5. Non-Functional Requirements

### 5.1 Security & Data Protection
- **NFR1: Data Privacy**: Personal ID documents and contact information must be stored securely and accessible only to authorized administrators.
- **NFR2: Duplicate Prevention**: The system must prevent duplicate registrations for the same event by the same user unless the previous registration was cancelled.

### 5.2 Usability & Accessibility
- **NFR3: Responsive Design**: The interface must be fully functional on both desktop and mobile browsers to accommodate users on the go.
- **NFR4: Real-time Feedback**: The system should provide immediate validation feedback for form inputs (e.g., email format, mandatory fields).

## 6. Assumptions & Dependencies
- **Dependency**: The application relies on the Frappe framework for core database and user management functions.
- **Assumption**: All events and room availability are maintained in the backend by Ashram administrators.

## 7. Approval & Sign-off
| Version | Description | Date | Status |
| :--- | :--- | :--- | :--- |
| 2.0 | Full Functional Requirements | 2025-12-21 | Draft |
