public static class Cluster{
  public float x, y, r;
  public static int id_tot = 0;
  public int id;
  public Cluster(float x, float y, float r){
    this.x = x;
    this.y = y;
    this.r = r;
    this.id = id_tot;
    id_tot++;
  }
}
