# How to Display Databricks Dashboards on OptiSigns

Article URL: https://support.optisigns.com/hc/en-us/articles/53952018650515-How-to-Display-Databricks-Dashboards-on-OptiSigns

### In this article, we'll walk you through setting up Databricks to display on your OptiSigns digital signs.

  * What You'll Need
  * Create a Service Principal Connection
    * In Databricks
    * In OptiSigns
  * Prepare Your Databricks Dashboard
    * Enable Dashboard Embed
    * Publish Dashboard
    * Share Dashboard with Service Principal
  * Create a Databricks App in OptiSigns
  * Deploying a Databricks App
  * Frequently Asked Questions

With the Databricks app, you can display a live **Databricks AI/BI dashboard** on any OptiSigns screen. 

Once set up, the dashboard renders automatically. It does not require a login on the screen, and it refreshes on a schedule you choose.

* * *

## What You'll Need

  * An OptiSigns account - [**Pro Plus Plan or higher**](<https://www.optisigns.com/pricing>)
  * A Databricks workspace (any tier), with Workspace admin access
  * A published AI/BI dashboard
  * An [OptiSigns-enabled device](<https://support.optisigns.com/hc/en-us/articles/360021855653-What-hardware-and-devices-are-supported>)
  * A screen, [set up and paired with OptiSigns](<https://support.optisigns.com/hc/en-us/articles/18823504383891-OptiSigns-Getting-Started-Guide>)

Within Databricks, you'll also need these four values: 

  * **Workspace URL**
  * **Workspace ID**
  * **Service Principal Client ID**
  * **Service Principal OAuth Secret**

We will show how to find them in the article below.

* * *

## Create a Service Principal Connection

A service principal (SP) is what OptiSigns uses to render the dashboard. This securely grants OptiSigns access to your published Dashboards without exposing any endpoints. 

### In Databricks

Create it in Databricks by clicking the workspace menu in the top right, then clicking **Settings:**

![](https://support.optisigns.com/hc/article_attachments/54089526933395)

### 

Open **Identity and access** , then find **Service principals** and hit **Manage**.

![](https://support.optisigns.com/hc/article_attachments/54089511420947)

Click Add service principal, then Add new service principal to account and workspace:

![](https://support.optisigns.com/hc/article_attachments/54089526939667)

Keep the default entitlements (**Consumer** , **Databricks SQL** , **Workspace** = On; **Admin** = Off) → **Add service principal:**

![](https://support.optisigns.com/hc/article_attachments/54089526941331)

Next, open the service principal. Your **Client ID** and **Secret** will show. Copy these values. You'll need them.

**NOTE**  
---  
These secrets are shown only once. Store them safely. If you lose the secret, you'll need to update your connection.  
  
The last two values you need are your **Workspace URL** and **Workspace ID.** These are both visible in your Databricks browser address bar (the ID is the `?o=` value).

[![](https://support.optisigns.com/hc/article_attachments/54089511430547)](<https://support.optisigns.com/optisigns/optisigns-smallapp/optisigns-smallapp-databricks/-/raw/feature/danling/databricks/docs/images/03-databricks-workspace-url-id.png>)

You can also find the Workspace ID in your workspace menu.

![](https://support.optisigns.com/hc/article_attachments/54089526942995)

You now have all **four values** the connection needs: Workspace URL, Workspace ID, Client ID, Secret.

### In OptiSigns

Go to **Integrations** under your main menu:

![](https://support.optisigns.com/hc/article_attachments/54089511434643)

Then, click the **Databricks tab** → **Add Databricks Connection**.

![](https://support.optisigns.com/hc/article_attachments/54089511435539)

Fill in the form:

![](https://support.optisigns.com/hc/article_attachments/54089526946323)

These values correspond to the In DataBricks section of this article.

  * **Name** — The name of the asset as displayed in OptiSigns. This will not display on your screen.
  * **Workspace URL** — The URL of the Workspace. 
  * **Workspace ID** — The ID of the Workspace.
  * **Service principal client ID** — The client ID of your created service principal. 
  * **Service principal OAuth secret** — The OAuth secret for your service principal.

Click **Add** to save the connection.

**NOTE**  
---  
One connection is equal to one Databricks workspace.  
  
If you have more than one workspace, add a separate connection for each.  
  
* * *

## Prepare Your Databricks Dashboard

Now that we've set up a Databricks connection, it's time to set up your Dashboard. This will grant the necessary permissions to OptiSigns, allowing you to display your Dashboard on a digital sign.

### Enable Dashboard Embed

Go to **Settings,** then **Security**.

Under **External access** , find **Embed dashboards and Genie Agents**.

Set it to Allow (embed on any domain), or Allow approved domains and add the OptiSigns player host: social-player.optisigns.com. Allow approved domains allows you to keep your embed private while still allowing OptiSigns to access it.

![](https://support.optisigns.com/hc/article_attachments/54089511438611)

Do **not** set it to **Deny** — that blocks embedding. On the Free Edition, this may be locked to Allow. This is fine, that's what we want.

### Publish Dashboard

Open the dashboard → **Publish** it (it must be Published, not a draft).

Choose a **data-permission mode**. Both options work with OptiSigns — pick the one that fits your needs:

  * **Share data permission (default)** — viewers run queries using the **publisher's credentials** , which enables a **shared cache** for performance.
  * **Individual data permission** — each viewer uses their **own data permission** to run queries, which can lead to **more frequent refresh operations**.

![](https://support.optisigns.com/hc/article_attachments/54089511440019)

Note that publishing is not the same as sharing. You will still need to share this Dashboard with our previously created service principal.

### Share Dashboard with Service Principal

Now we'll get the published dashboard shared with our service principal. 

On the dashboard, click **Share**. Add the **service principal your connection uses** with **CAN RUN** (or CAN MANAGE).

[![](https://support.optisigns.com/hc/article_attachments/54089511441811)](<https://support.optisigns.com/optisigns/optisigns-smallapp/optisigns-smallapp-databricks/-/raw/feature/danling/databricks/docs/images/05-databricks-share-service-principal.png>)

Make sure the service principal can access the **data** the dashboard uses.

Back in OptiSigns, **reopen the app config** (or re-select the connection) so the dashboard list refreshes.

* * *

## Create a Databricks App Within OptiSigns

Now that we've got our service principal connection and dashboard(s) prepared, we need to actually set them up as Assets within OptiSigns.

To do this, open OptiSigns and go to **Files/Assets** → **Apps** → **Databricks**.

![](https://support.optisigns.com/hc/article_attachments/54089511443091)

You'll open up the Databricks app and need to fill in some required information:

![](https://support.optisigns.com/hc/article_attachments/54089526955283)

  * **Name -** The name of your Databricks app. This is for use in OptiSigns and will not display on your screen.
  * **Databricks Connection -** Choose from any Databricks connections you've set up.
  * **Dashboard -** Choose from a list of dashboards associated with this connection.
  * **Display**
    * **Refresh (seconds) -** How often you want to refresh the Dashboard. This can be as low as 30s or as high as 3600s. Note that this will cause OptiSigns to fetch updated data, meaning it will flash on your display. More frequent updates will cause more load on the Databricks warehouse.

* * *

## Deploying a Databricks App

You can deploy your new Databricks app as an individual asset, or as part of a [Split Screen](<https://support.optisigns.com/hc/en-us/articles/360026559573-How-to-Create-and-Use-the-Split-Screen-App>).

To get your new Databricks asset to a screen, go to the **Screens** tab, then click the screen you want to assign it to.

[![](https://support.optisigns.com/hc/article_attachments/54089526956179)](<https://support.optisigns.com/hc/article_attachments/53028011480979>)

This brings us to the **Edit Screen** tab:

[![](https://support.optisigns.com/hc/article_attachments/54089511451283)](<https://support.optisigns.com/hc/article_attachments/53027988865171>)

Here, select **Asset** under Content type. If you already have an Asset, Playlist, or Schedule selected, you can hit **Change**.

Then, select your created Databricks Asset.

Now hit **Save**. Your Databricks asset will now display on screen. 

You can also deploy it as part of a split screen, allowing you to show other assets at the same time. See how in our [Split Screen app article.](<https://support.optisigns.com/hc/en-us/articles/360026559573-How-to-Create-and-Use-the-Split-Screen-App>) It can also be displayed in a Playlist or Schedule.

### How Updates will Appear Onscreen

When you republish your dashboard within Databricks, your changes will appear within one refresh interval.

Your dashboard shows Databricks' cached query results. For the newest data, we recommend you set up a scheduled refresh of the dashboard within Databricks. Your screen will then display the latest results on its next refresh.

* * *

## Frequently Asked Questions

Here, we'll answer some frequently asked questions our customers have, and solve some common troubleshooting issues.

#### My Dashboard list is empty, or I can't find my Dashboard when configuring the app. How can I make them appear?

This is usually caused when your dashboard isn't shared with your service principal. Ensure the published dashboard is shared with the service principal the connection uses. It should say "CAN RUN". When it does, reopen the picker.

Additionally, make sure the connection you're using matches the workspace where the dashboard lives.

#### My screen is showing "reach out to your workspace administrator." How can I solve this?

This is caused by one of two things:

  1. Embedding isn't enabled, or
  2. The OptiSigns host isn't allowed

Make sure you've enabled Embedding, and set Embed dashboards to Allow within Databricks. You can, alternatively, make sure "social-player.optisigns.com" is under Allow approved domains.

#### My connection won't save or my verification fails. What can I do?

This means that you've input either the wrong Client ID / Secret, or the wrong Workspace URL / Workspace ID. Re-copy them from Databricks.

Note that the secret is shown only once. You may need to regenerate it if it is lost.

#### My screen is showing an old dashboard and isn't refreshing. Why not?

Your layout updates on the next refresh interval. Additionally, when updates to your Dashboard are made, they need to be published in Databricks (not just saved as a draft). After publishing, wait one interval.

You can always refresh your screen manually to get the latest update.

#### My Databricks dashboard used to display fine, but stopped all of a sudden! What's wrong?

Usually, this has to do with an expired or rotated service principal secret. Try generating a new secret within Databricks and updating your OptiSigns connection.

### That's all!

OptiSigns is a leader in [digital signage software](<https://www.optisigns.com/>). If you have any additional questions, concerns or any feedback about OptiSigns or getting Snowflake to work on it, feel free to reach out to our support team at [support@optisigns.com](<mailto:support@optisigns.com>).
