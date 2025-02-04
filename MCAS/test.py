import csv
from rouge_score import rouge_scorer
from bert_score import score

# Sample Data: Replace with your dataset
reference_summaries = [
    "The video chronicles the process of painting a motorcycle with a custom color scheme, from surface preparation to the application of base coats, layers, and a protective clear finish.",
    "Victoria West shares a holistic system for curing acne naturally, based on her personal experience and extensive research. The video emphasizes non-conventional treatments and overall skin health.",
    "A baking tutorial shows how to create checkerboard cookies using two types of dough. The video demonstrates layering, shaping, and baking techniques for these visually appealing treats.",
    "The tutorial demonstrates making a cherry blossom charm using loom bands without a loom, focusing on creating heart-shaped petals and assembling the flower with a stem.",
    "A practical guide on applying Plasti Dip to motorcycle rims, covering preparation, spraying techniques, and achieving a glossy finish with Plasti Dip Enhancer.",
    "In this baking tutorial, Hany from Hana’s YouTube channel demonstrates how to make PlayStation controller button-themed desserts. The process begins with preparing a German buttercream filling and a basic sponge cake, which is baked, cooled, and cut into small round pieces. The rounds are then filled with buttercream and refrigerated until firm. Next, fondant decorations are created by cutting out small circles and attaching additional details with a lightly moistened brush. A ganache is prepared by heating heavy cream and mixing it with chocolate, and the cakes are dipped into it before being topped with the fondant decorations. Finally, royal icing in pink, blue, red, and green is used to create the PlayStation button symbols (triangle, circle, X, and square). Hany mentions that these desserts can be made in advance and stored in the fridge for a few days. "
]

generated_summaries = [
    "Roylott v-twins to be AIDS preps for exterior paint job. The video highlights the process of preparing the tank, fenders, and rear fenders for a black finish. The creator uses anti-corrosive primer, scuff pads, and tape to prevent paint from sticking. After preparing the tank, fenders, and rear fenders, Roylott sprayed a gloss black base coat to give the tank a smooth, black finish. The creator uses a jig to create a base coat, followed by spraying the paint with a base coat. The process involves preparing the garage, preparing the fenders, and cleaning the fixtures. The creator also shares tips for maintaining the garage's appearance. This video demonstrates how to apply Sherwin Williams Dimension Base Coat to a Sherwin Williams Dimension Cup. The process involves applying two to three medium coats of base coat, ensuring that the surface is able to see through the base coat. The process involves sanding the surface to remove any imperfections, and applying clear coat to ensure a smooth finish. The video emphasizes the importance of ensuring the surface is clean and free of debris.",
    "Victoria West shares her experience with acne, focusing on holistic medicine and natural healing. She shares her experience with irritated skin and acne on her face shoulders and back, and shares her holistic approach to treating acne. She shares her research and experiences with natural remedies, including Chinese healers, nutritionists, and natural fats. The video emphasizes non-conventional treatments and overall skin health.",
    "This tutorial demonstrates how to make chocolate cookies using a dough recipe. The dough is shaped into rectangles, rolled, and baked. The dough is rolled into squares, cut into circles, and baked. The cookies are cooled before baking. The tutorial emphasizes the importance of maintaining the shape of the cookies to avoid burns. The cookies are baked at 18 180°C or 350°F for 15 to 20 minutes.",
    "This tutorial demonstrates how to make a cherry blossom charm without a rain balloon. The charm is made using 15 petals and a single green rubber band for the stem. The charm is easy to make and can be customized with different colors. The creator demonstrates how to create the petals using a crochet hook and a petal color. The creator also shows how to create the petals using a single green rubber band. This video demonstrates how to create a slip knot using a flower. ",
    "This video demonstrates how to apply Plastic Dip to a motorcycle rim. The process involves cleaning the rim, preparing it for spraying, and preparing it for painting. The video emphasizes the importance of ensuring the rim is ventilated, and avoiding sun exposure.",
    "In this video, Any from hands shows how to make PlayStation controller buttons bet Force dessert. The recipe includes making sponge cake, German buttercream filling, and fondant decorations. The video also includes tips for preparing fondant decorations, including moistening the fondant with a brush, and preparing panache, including pouring it over the cakes, and dipping it into the panache.  The panache is still wet, but the decoration can be placed on top. The cake is then placed in the fridge for a few days before panache sets. The creator also uses royal icing for the buttons and explains how to prepare the panache for the decorations."
]

# Initialize ROUGE scorer
rouge = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)

# Compute BERTScore
P, R, F1 = score(generated_summaries, reference_summaries, lang="en", model_type="bert-base-uncased")

# Open CSV file to store results
csv_filename = "summary_evaluation_results.csv"
with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    
    # Write header
    writer.writerow(["Reference Summary", "Generated Summary",
                     "ROUGE-1 (F1)", "ROUGE-2 (F1)", "ROUGE-L (F1)",
                     "BERT Precision", "BERT Recall", "BERT F1"])

    # Process each summary pair
    for i in range(len(reference_summaries)):
        rouge_scores = rouge.score(reference_summaries[i], generated_summaries[i])

        # Write row to CSV
        writer.writerow([
            reference_summaries[i], generated_summaries[i],
            round(rouge_scores["rouge1"].fmeasure, 4),
            round(rouge_scores["rouge2"].fmeasure, 4),
            round(rouge_scores["rougeL"].fmeasure, 4),
            round(P[i].item(), 4), round(R[i].item(), 4), round(F1[i].item(), 4)
        ])

print(f"✅ Evaluation completed! Results saved to: {csv_filename}")
