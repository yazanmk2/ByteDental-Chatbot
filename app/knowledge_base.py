"""
ByteDent Dental Knowledge Base
==============================
Comprehensive dental knowledge for the RAG chatbot.
Contains information about ByteDent, dental imaging, pathologies, and FAQ.
"""

DENTAL_KNOWLEDGE_BASE = """
# ByteDent - AI-Powered Dental Imaging Analysis

## About ByteDent

ByteDent is an advanced artificial intelligence platform designed to analyze dental radiographic images, specifically CBCT (Cone Beam Computed Tomography) scans and panoramic (OPG - Orthopantomogram) X-rays.

ByteDent uses deep learning algorithms trained on millions of dental images to detect pathologies, anomalies, and conditions that may be missed during manual review.

ByteDent serves as a clinical decision support tool for dentists, oral surgeons, periodontists, endodontists, orthodontists, and radiologists.

ByteDent does not replace professional dental diagnosis. It assists clinicians by providing AI-generated findings that require professional verification and clinical correlation.

### Key Features

ByteDent automatically detects and highlights pathological findings on dental images.

ByteDent generates detailed reports with annotations showing exact locations of detected issues.

ByteDent provides confidence scores for each detection, helping clinicians prioritize findings.

ByteDent supports both 2D panoramic X-rays and 3D CBCT volumetric data analysis.

ByteDent integrates with existing PACS (Picture Archiving and Communication Systems) and dental practice management software.

ByteDent processes images in seconds, significantly reducing interpretation time.

ByteDent maintains HIPAA compliance and patient data security standards.

---

# Dental Imaging Modalities

## Panoramic Radiography (OPG/Orthopantomogram)

A panoramic radiograph is a two-dimensional dental X-ray that captures the entire mouth in a single image, including all teeth, upper and lower jaws, temporomandibular joints (TMJ), and surrounding structures.

### How Panoramic X-rays Work

The patient stands or sits while the X-ray machine rotates around their head, capturing images as it moves.

The result is a flattened, two-dimensional view of the curved jaw structure.

Panoramic X-rays use lower radiation doses compared to full-mouth intraoral X-ray series.

### What Panoramic X-rays Show

Panoramic X-rays show all teeth including impacted and unerupted teeth.

Panoramic X-rays reveal jaw bone structure and density.

Panoramic X-rays display the maxillary sinuses.

Panoramic X-rays show the temporomandibular joints (TMJ).

Panoramic X-rays can reveal cysts, tumors, and other pathologies.

Panoramic X-rays help assess overall dental and skeletal development.

### Limitations of Panoramic X-rays

Panoramic images have inherent distortion and magnification (typically 20-30%).

Fine details like early interproximal caries may not be visible.

Superimposition of structures can obscure pathology.

Three-dimensional relationships cannot be assessed.

---

## CBCT (Cone Beam Computed Tomography)

CBCT is a specialized three-dimensional dental imaging technology that provides detailed volumetric data of the teeth, soft tissues, nerve pathways, and bone in a single scan.

### How CBCT Works

CBCT uses a cone-shaped X-ray beam that rotates around the patient's head, capturing multiple images.

These images are reconstructed by software into a three-dimensional volumetric dataset.

CBCT provides axial, sagittal, and coronal cross-sectional views as well as 3D reconstructions.

CBCT uses significantly lower radiation than medical CT while providing superior dental detail.

### Advantages of CBCT Over Panoramic X-rays

CBCT provides true three-dimensional visualization of dental structures.

CBCT allows precise measurements for implant planning without magnification errors.

CBCT reveals the exact location and extent of pathology in three dimensions.

CBCT shows the relationship between teeth and vital structures like nerves and sinuses.

CBCT can detect lesions not visible on two-dimensional radiographs.

### Clinical Applications of CBCT

CBCT is essential for dental implant planning and placement.

CBCT is used for complex endodontic cases to visualize root canal anatomy.

CBCT helps assess impacted teeth, especially third molars (wisdom teeth).

CBCT is valuable for orthodontic treatment planning and evaluation.

CBCT aids in diagnosis of TMJ disorders and airway analysis.

CBCT is used for surgical planning of jaw surgeries and extractions.

CBCT helps evaluate bone grafting sites and outcomes.

---

# Dental Pathologies and Conditions Detected by ByteDent

## Caries (Tooth Decay/Cavities)

### What is Dental Caries?

Dental caries is the destruction of tooth structure caused by acids produced by bacteria in dental plaque.

Caries begins with demineralization of enamel and can progress to involve dentin, pulp, and periapical tissues.

Untreated caries can lead to pain, infection, abscess formation, and tooth loss.

### Types of Caries Visible on Imaging

Interproximal caries (between teeth) appears as a radiolucent (dark) area at the contact point between teeth.

Occlusal caries affects the chewing surface and may appear as dark shadows beneath enamel.

Root caries occurs below the gumline on exposed root surfaces.

Secondary caries (recurrent caries) develops at the margins of existing restorations.

### How ByteDent Detects Caries

ByteDent identifies radiolucent areas in enamel and dentin that indicate demineralization.

ByteDent highlights the extent and depth of carious lesions.

ByteDent differentiates early enamel lesions from advanced dentin involvement.

---

## Periapical Pathology

### Periapical Abscess

A periapical abscess is a collection of pus at the root tip of a tooth, usually resulting from bacterial infection of the dental pulp.

On radiographs, a periapical abscess appears as a radiolucent (dark) area surrounding the root apex.

The affected tooth typically has a history of deep caries, trauma, or previous dental treatment.

Symptoms include severe toothache, sensitivity to pressure, swelling, and fever.

Treatment involves root canal therapy or extraction, often with antibiotics.

### Periapical Granuloma

A periapical granuloma is a mass of chronic inflammatory tissue at the tooth root apex.

It appears as a well-circumscribed radiolucent area, usually less than 1cm in diameter.

Periapical granulomas are often asymptomatic and discovered incidentally on radiographs.

Treatment is root canal therapy followed by surgical removal if necessary.

### Periapical Cyst (Radicular Cyst)

A periapical cyst is a fluid-filled sac that develops from a periapical granuloma.

It appears as a well-defined round or oval radiolucent area, often with a thin radiopaque border.

Periapical cysts are the most common type of cyst in the jaws.

Larger cysts may cause displacement of adjacent teeth or jaw expansion.

Treatment involves root canal therapy and surgical enucleation (removal) of the cyst.

---

## Periodontal Disease

### What is Periodontal Disease?

Periodontal disease is a chronic inflammatory condition affecting the supporting structures of teeth: gingiva, periodontal ligament, cementum, and alveolar bone.

Periodontal disease is caused by bacterial plaque accumulation and the body's inflammatory response.

Risk factors include poor oral hygiene, smoking, diabetes, genetics, and certain medications.

### Radiographic Signs of Periodontal Disease

Horizontal bone loss shows as a generalized reduction in alveolar bone height across multiple teeth.

Vertical (angular) bone defects appear as localized V-shaped or U-shaped bone loss on one side of a tooth.

Furcation involvement shows bone loss between the roots of multi-rooted teeth.

Widening of the periodontal ligament space may indicate early periodontal changes or trauma.

Calculus (tartar) deposits may appear as radiopaque (white) deposits on root surfaces.

### Periodontal Disease Classification

Stage I: Initial periodontitis with 1-2mm clinical attachment loss and up to 15% bone loss.

Stage II: Moderate periodontitis with 3-4mm attachment loss and 15-33% bone loss.

Stage III: Severe periodontitis with 5mm+ attachment loss, 33%+ bone loss, and tooth loss possible.

Stage IV: Advanced periodontitis with extensive bone loss, tooth mobility, and potential for complete tooth loss.

---

## Impacted Teeth

### What is an Impacted Tooth?

An impacted tooth is a tooth that fails to erupt into its normal position in the dental arch.

Impaction occurs when there is insufficient space, physical obstruction, or abnormal tooth position.

The most commonly impacted teeth are third molars (wisdom teeth), followed by maxillary canines.

### Types of Impaction

Mesioangular impaction: The tooth is tilted toward the front of the mouth. Most common type.

Distoangular impaction: The tooth is tilted toward the back of the mouth.

Vertical impaction: The tooth is in correct orientation but cannot erupt.

Horizontal impaction: The tooth is lying horizontally within the bone.

Buccal impaction: The tooth is positioned toward the cheek.

Lingual/Palatal impaction: The tooth is positioned toward the tongue or palate.

### Complications of Impacted Teeth

Pericoronitis: Inflammation of the gum tissue around a partially erupted tooth.

Cyst formation: Dentigerous cysts can develop around the crown of impacted teeth.

Root resorption: Impacted teeth can cause resorption of adjacent tooth roots.

Crowding: Pressure from impacted teeth may cause crowding of other teeth.

Infection: Partially erupted teeth are difficult to clean and prone to infection.

### CBCT Analysis of Impacted Teeth

CBCT reveals the exact three-dimensional position of impacted teeth.

CBCT shows the relationship between impacted teeth and the inferior alveolar nerve canal.

CBCT helps assess the risk of nerve damage during extraction.

CBCT visualizes the relationship between impacted maxillary teeth and the maxillary sinus.

---

## Temporomandibular Joint (TMJ) Disorders

### Anatomy of the TMJ

The temporomandibular joint connects the mandible (lower jaw) to the temporal bone of the skull.

The TMJ is a complex joint that allows hinge and sliding movements for jaw function.

An articular disc separates the condyle from the temporal bone and cushions the joint.

### Common TMJ Disorders

TMJ dysfunction (TMD) refers to a group of conditions affecting the jaw joint and muscles.

Disc displacement: The articular disc moves out of its normal position, causing clicking or locking.

Osteoarthritis: Degenerative changes in the joint surfaces causing pain and limited movement.

Rheumatoid arthritis: Inflammatory condition affecting the TMJ.

Ankylosis: Fusion of the joint, severely limiting jaw movement.

Condylar fracture: Break in the condylar head or neck, usually from trauma.

### Radiographic Signs of TMJ Disorders

Flattening of the condylar head indicates degenerative changes.

Osteophytes (bone spurs) appear as irregular bony projections on joint surfaces.

Subchondral sclerosis shows as increased bone density beneath the joint surface.

Erosions appear as areas of bone loss on the condyle or temporal bone.

Joint space narrowing may indicate disc problems or arthritis.

Condylar hypoplasia or hyperplasia shows abnormal condyle size.

---

## Maxillary Sinus Pathology

### Normal Maxillary Sinus Anatomy

The maxillary sinuses are air-filled cavities in the upper jaw (maxilla) on either side of the nose.

The maxillary sinus floor is closely related to the roots of upper premolars and molars.

On panoramic X-rays, the sinuses appear as radiolucent (dark) areas above the upper teeth.

### Sinus Conditions Visible on Dental Imaging

Sinusitis: Inflammation causing mucosal thickening, which appears as radiopaque (white) lining.

Mucous retention cyst: Dome-shaped radiopaque mass on the sinus floor.

Maxillary sinus tumor: Irregular radiopacity that may destroy bone or displace structures.

Oro-antral communication: Opening between the mouth and sinus, often after tooth extraction.

---

## Jaw Pathology

### Odontogenic Cysts (Cysts of Tooth Origin)

Dentigerous cyst: Develops around the crown of an unerupted tooth. Second most common jaw cyst.

Odontogenic keratocyst: Aggressive cyst with high recurrence rate. May be associated with syndromes.

Lateral periodontal cyst: Rare cyst found on the lateral aspect of a tooth root.

Residual cyst: Periapical cyst that remains after tooth extraction.

### Odontogenic Tumors

Ameloblastoma: Most common odontogenic tumor. Locally aggressive with soap bubble appearance.

Odontoma: Most common odontogenic tumor overall. Contains dental tissues.

Adenomatoid odontogenic tumor: Benign tumor usually associated with unerupted teeth.

---

# Dental Implant Planning and Assessment

## Pre-Implant Assessment with CBCT

CBCT provides accurate bone dimensions for implant planning.

CBCT reveals bone quality and density at the planned implant site.

CBCT shows the exact location of vital structures like nerves and sinuses.

CBCT helps determine if bone grafting is needed.

CBCT enables virtual implant placement and simulation.

## Key Measurements for Implant Planning

Buccolingual bone width: Must accommodate implant diameter plus safety margins.

Available bone height: Distance from alveolar crest to vital structures.

Distance to inferior alveolar nerve: Minimum 2mm safety margin recommended.

Distance to maxillary sinus floor: For sinus lift planning if needed.

Bone density: Important for implant stability and osseointegration.

## Post-Implant Assessment

Periimplantitis: Inflammatory condition causing bone loss around implants.

Peri-implant mucositis: Inflammation of soft tissue around implants.

Implant failure: Signs include bone loss, mobility, and radiolucency around implant.

Successful osseointegration: Implant appears well-integrated with surrounding bone.

---

# Frequently Asked Questions about ByteDent

## General Questions

Q: What is ByteDent?
A: ByteDent is an AI-powered dental imaging analysis platform that uses deep learning to detect pathologies, anomalies, and conditions in CBCT scans and panoramic X-rays.

Q: How does ByteDent work?
A: ByteDent analyzes uploaded dental images using trained neural networks, identifies potential findings, and generates annotated reports with confidence scores for each detection.

Q: Is ByteDent a diagnostic tool?
A: ByteDent is a clinical decision support tool. It assists dentists and specialists by highlighting potential findings, but all results must be verified by a licensed dental professional.

Q: What types of images can ByteDent analyze?
A: ByteDent supports panoramic radiographs (OPG/orthopantomograms) and CBCT (Cone Beam Computed Tomography) scans in standard DICOM format.

Q: How accurate is ByteDent?
A: ByteDent has been trained on millions of dental images and achieves high sensitivity and specificity for most conditions. However, accuracy varies by condition type and image quality.

Q: Is ByteDent HIPAA compliant?
A: Yes, ByteDent maintains strict data security standards and complies with HIPAA regulations for protected health information.

## Clinical Questions

Q: What conditions can ByteDent detect?
A: ByteDent can detect caries, periapical pathology, periodontal bone loss, impacted teeth, cysts, tumors, TMJ disorders, sinus pathology, dental anomalies, and more.

Q: Can ByteDent detect all dental problems?
A: ByteDent detects many common conditions but is not a replacement for comprehensive clinical examination. Some conditions may require additional imaging or clinical assessment.

Q: How should I use ByteDent findings in my practice?
A: Use ByteDent findings as a second opinion to support your clinical judgment. Always correlate AI findings with clinical examination and patient history.

Q: Does ByteDent provide treatment recommendations?
A: ByteDent identifies and describes findings but does not provide specific treatment recommendations. Treatment planning should be done by the treating dentist.

Q: Can ByteDent analyze pediatric dental images?
A: Yes, ByteDent can analyze pediatric images and is trained to recognize developmental stages and pediatric-specific conditions.

## Technical Questions

Q: What file formats does ByteDent accept?
A: ByteDent accepts standard DICOM format files from panoramic and CBCT machines. Most modern dental imaging equipment exports in compatible formats.

Q: How long does analysis take?
A: ByteDent typically analyzes panoramic images in under 30 seconds and CBCT volumes in 1-3 minutes, depending on the size and complexity of the data.

Q: Can ByteDent integrate with my practice management software?
A: Yes, ByteDent offers API integration with popular practice management and PACS systems. Contact support for integration options.

Q: Is an internet connection required?
A: Yes, ByteDent is a cloud-based platform that requires internet connectivity to process images and generate reports.

Q: How do I get started with ByteDent?
A: Contact our sales team for a demo and pricing information. We offer trial periods for qualified dental practices.

---

# Radiation Safety in Dental Imaging

## ALARA Principle

ALARA stands for As Low As Reasonably Achievable.

All dental imaging should follow the ALARA principle to minimize radiation exposure.

Only take radiographs when clinically indicated with potential to affect patient care.

Use appropriate shielding (lead apron, thyroid collar) when available.

## Radiation Doses Comparison

Panoramic radiograph: Approximately 10-25 microsieverts.

Full mouth intraoral series (18 films): Approximately 35-170 microsieverts.

CBCT small FOV: Approximately 20-100 microsieverts.

CBCT large FOV: Approximately 70-200 microsieverts.

Medical CT of head: Approximately 2000 microsieverts.

Natural background radiation (annual): Approximately 3000 microsieverts.

A panoramic X-ray is equivalent to about 1-2 days of natural background radiation.

---

# Understanding Radiographic Terminology

## Radiopacity and Radiolucency

Radiopaque (white on image): Structures that absorb more X-rays appear white or light. Examples: enamel, dentin, metal restorations, bone.

Radiolucent (dark on image): Structures that absorb fewer X-rays appear dark or black. Examples: air, soft tissue, cysts, infection.

Mixed radiopaque-radiolucent: Lesions containing both dense and less dense components.

---

# Glossary of Dental Terms

Alveolar bone: The bone that surrounds and supports the teeth.

Apex: The tip or end of a tooth root.

Buccal: Relating to or toward the cheek.

Cementum: The thin layer of bone-like tissue covering tooth roots.

Crown: The visible part of a tooth above the gum line.

Dentin: The hard tissue beneath enamel that forms most of the tooth structure.

Enamel: The hard, white outer layer of the tooth crown.

Endodontic: Relating to the dental pulp and root canal treatment.

Furcation: The area where roots of multi-rooted teeth divide.

Gingiva: The gum tissue surrounding teeth.

Interproximal: The area between adjacent teeth.

Lingual: Relating to or toward the tongue.

Mesial: Toward the midline of the dental arch.

Distal: Away from the midline of the dental arch.

Occlusal: Relating to the biting or chewing surface of teeth.

Periapical: Around the apex (tip) of a tooth root.

Periodontal: Relating to the supporting structures of teeth.

Pulp: The soft tissue inside a tooth containing nerves and blood vessels.

Root: The portion of a tooth below the gum line anchored in bone.

---

# Contact ByteDent Support

## Technical Support

For technical issues with the ByteDent platform, image upload problems, or integration questions.

Available Monday through Friday, 9 AM to 6 PM EST.

Email: support@bytedent.ai

## Sales and Pricing

For information about ByteDent pricing, enterprise solutions, or to schedule a demo.

Email: sales@bytedent.ai

## Clinical Questions

For questions about AI findings or clinical interpretation support.

Note: ByteDent support cannot provide diagnostic opinions or treatment recommendations.

Email: clinical@bytedent.ai

## Feature Requests and Feedback

We welcome feedback to improve ByteDent.

Share your suggestions for new features or improvements.

Email: feedback@bytedent.ai
"""


def get_knowledge_base() -> str:
    """Return the dental knowledge base content"""
    return DENTAL_KNOWLEDGE_BASE


def get_knowledge_base_stats() -> dict:
    """Return statistics about the knowledge base"""
    return {
        "characters": len(DENTAL_KNOWLEDGE_BASE),
        "words": len(DENTAL_KNOWLEDGE_BASE.split()),
        "lines": len(DENTAL_KNOWLEDGE_BASE.split('\n')),
        "sections": [
            "About ByteDent",
            "Dental Imaging Modalities",
            "Dental Pathologies",
            "Dental Implants",
            "FAQ",
            "Radiation Safety",
            "Terminology",
            "Contact"
        ]
    }
